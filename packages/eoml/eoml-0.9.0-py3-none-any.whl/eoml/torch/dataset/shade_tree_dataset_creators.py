"""Dataset creation utilities for shade and tree detection from satellite imagery.

This module provides tools for creating training datasets that combine high-resolution
shade/tree annotations with lower-resolution satellite imagery. Handles spatial alignment,
temporal matching, and preprocessing of multi-source geospatial data.
"""

import contextlib
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import numpy as np
import rasterio

from libterra_gis.environement import get_write_profile, get_read_profile
from libterra_gis.raster_utils import RasterImage
from libterra_gis.shade.heuristic import extract_soil, post_process_hand_cleaned
from eoml.raster.band import Band
from eoml.raster.raster_reader import AbstractRasterReader, append_raster_reader, RasterReader
from eoml.torch.cnn.torch_utils import aligned_bound
from eoml.torch.cnn.training_dataset import BasicTrainingDataset, BasicYearTrainingDataset
from rasterio.enums import Resampling
from rasterio.windows import Window
from torch.utils.data import Dataset, random_split

logger = logging.getLogger(__name__)


class ShadeMatchNNInput(Dataset):
    """Match and align high-resolution annotations with satellite imagery for CNN training.

    Creates training datasets by spatially aligning high-resolution shade/tree annotations
    with corresponding satellite imagery, handling different resolutions and projections.
    Supports temporal matching when multiple acquisition dates are available.

    Attributes:
        input_raster_reader (AbstractRasterReader or dict): Reader(s) for satellite imagery.
            Can be single reader or dict mapping years to readers for temporal matching.
        size (int): Kernel/window size for CNN.
    """

    def __init__(self,
                 input_raster_reader: AbstractRasterReader | dict[int, AbstractRasterReader],
                 size: int):
        """Initialize ShadeMatchNNInput.

        Args:
            input_raster_reader (AbstractRasterReader or dict): RasterReader for satellite
                imagery, or dict mapping years to readers for temporal datasets.
            size (int): Size of CNN input window.
        """

        self.input_raster_reader: AbstractRasterReader | dict[int, AbstractRasterReader] = input_raster_reader
        self.size: int = size

    def _input_windows(self, input, raw, precision=0.01):
        """
         Compute the input windows with a shrink of 1 pixel.
         We assume pixel is area. pixel "point" is located at the top left of the pixel and bounding is the real bounding
          box. This mean boding box is effectively at pixel (0, 0) and (length, length). the actual array pixel as last
          pixel at length-1, length-1

          the pixel is included if precision percent of it is covered by the raw raster
          """
        (left, bottom, right, top) = rasterio.warp.transform_bounds(raw.crs, input.crs, *raw.bounds)

        return aligned_bound(left, bottom, right, top, input.transform, precision)

    def mask(self, value, bound, mask: AbstractRasterReader, transformer):
        """Act on the stacked raster """
        mask_data=None
        if mask is not None:
            with mask:
                mask_data = mask.read_bound(bound)

        masked = transformer(value, mask_data)

        return masked

    def generate_target_raster(self, nn_out_readers, nn_input_raster, path, mask=None, mask_f=None, save_all=False,
                               precision=0.01):
        """
        Generate the target raster (the ideal output of the nn network
        :param nn_out_readers:
        :param nn_out_readers:
        :param path:
        :param mask: extra information used to mask given pixel
        :param mask_f: function used to mask pixel
        :param save_all:
        :param precision:
        :return:
        """
        out = []
        half = self.size // 2

        # sentinel we want to reproject to
        target = nn_input_raster.ref_raster_info()
        # nn output
        src = nn_out_readers.ref_raster_info()
        n_bands = nn_out_readers.n_band

        windows = self._input_windows(target, src, precision=precision)

        sample_raster_reader = append_raster_reader([nn_input_raster, nn_out_readers],
                                                    0,
                                                    nn_input_raster.read_profile)

        windows = Window(windows.col_off - half, windows.row_off - half, windows.width + self.size,
                         windows.height + self.size)

        with sample_raster_reader:
            values = sample_raster_reader.read_windows(windows)

            #remove non output value
            if not save_all:
                values = values[-n_bands:]

        if mask_f is not None:
            bounds = target.window_bounds(windows)
            values = self.mask(values, bounds, mask, mask_f)

        out.append(values)

        self.export_result(values, target.window_transform(windows), target.crs, path)

        return out

    def export_result(self, values, transform, crs, out_path):

        write_profile = get_write_profile()
        write_profile.update({
            'transform': transform,
            'width': values.shape[2],
            'height': values.shape[1],
            'count': values.shape[0],
            'dtype': "float32",
            'crs': crs,
            'nodata': 255})

        with rasterio.open(out_path, 'w', **write_profile) as src:
            src.write(values)

    def create_nn_output(self,
                         in_folder,
                         out_folder,
                         transformer=None,
                         mask=None,
                         mask_f=None,
                         save_all=True,
                         read_profile=None,
                         sharing=True):

        file_out = []
        date_out = []

        if read_profile is None:
            read_profile = get_read_profile()

        output_rasters, dates = self.get_outputs_raster(in_folder)

        Path(out_folder).mkdir(parents=True, exist_ok=True)

        for out_raster, date in zip(output_rasters, dates):
            raster_name = Path(out_raster).stem

            out_raster_reader = RasterReader(out_raster,
                                             Band.from_file(out_raster),
                                             transformer,
                                             Resampling.average,
                                             read_profile,
                                             sharing)

            out_p = f"{out_folder}/{raster_name}.tif"

            if isinstance(self.input_raster_reader, dict):
                # if raster is not available at date skip
                nn_input_raster = self.input_raster_reader.get(date, None)
            else:
                nn_input_raster = self.input_raster_reader

            if nn_input_raster is not None:
                self.generate_target_raster(out_raster_reader,
                                            nn_input_raster,
                                            out_p,
                                            mask=mask, mask_f=mask_f, save_all=save_all)

                file_out.append(out_p)
                date_out.append(date)
            else:
                logger.info(f"skipping {out_raster} at year {date}")

        return file_out, date_out

    def get_outputs_raster(self, in_folder) -> (list[str], list[datetime]):
        """ read the raster and date in the input folder"""
        tif_path = []
        dates = []

        tifs = [f.path for f in os.scandir(in_folder) if f.name.endswith('.tif')]
        for tif in tifs:
            logger.info(f"reading date for {tif}")
            tif_path.append(tif)
            dates.append(self._read_date(f'{tif[:-4]}.txt'))

        return tifs, dates

    def _read_date(self, date):
        with open(date, "r") as f:
            for line in f.readlines():
                before, match, after = line.partition(":")
                if before.strip() == 'date':
                    return datetime.strptime(after.strip(), '%d/%m/%Y').year

            raise "no date found"


class DatasetPostProcessor:
    """"""

    def __init__(self, image_post_processor):

        self.image_post_processor = image_post_processor

    def process_folder(self,
                       in_folder,
                       out_folder,
                       targets=('shade.tif', 'soil.tif'),
                       reference='google.tif',
                       mode="match",
                       info=None,
                       outname=None, ):
        """

        :param in_folder: folder containing the sample, it will be recursively scanned
        :param out_folder:
        :param targets:
        :param reference: input containing the geo-location information
        :param mode: using mode="match",same in and out folder (will just add the file to the folder),
                     mode is "one" = all in one folder or "same" == same file structure
        :param info:
        :param outname:
        :return:
        """

        # create the new folder and put all the image in one folder
        if mode == "one":
            Path(out_folder).mkdir(parents=True, exist_ok=True)

        save_folder = out_folder

        #return object with more info keep only name
        dirs = [f.name for f in os.scandir(in_folder) if f.is_dir()]
        for dir in dirs:
            logger.info(f"processing {dir}")
            # We use the same folder and put each image in a different folder
            # if we use one we put everything in out_folder

            f_outname = None
            if mode == "match":
                save_folder = os.path.join(out_folder, dir)
                Path(save_folder).mkdir(parents=True, exist_ok=True)
                # name is just out name or folder name
                f_outname = f'{outname}' if outname is not None else f'{dir}'

            if mode == "one":
                # we add dir name to separe file
                f_outname = f'{dir}_{outname}' if outname is not None else f'{dir}'

            if f_outname is None:
                raise "mode should be match or one"

            if isinstance(targets, (list, tuple)):
                targets_full_p = [os.path.join(in_folder, dir, f) for f in targets]
            else:
                targets_full_p = [os.path.join(in_folder, dir, targets)]

            reference_full_p = os.path.join(in_folder, dir, reference)

            out_path = os.path.join(save_folder, f'{f_outname}.tif')

            logger.info(f"saving at {out_path}")
            raster = self.image_post_processor.process(targets_full_p, reference_full_p)
            raster.save(out_path)

            if info is not None:
                if mode == "same":
                    shutil.copyfile(os.path.join(in_folder, dir, info), os.path.join(save_folder, info))
                else:
                    shutil.copyfile(os.path.join(in_folder, dir, info), os.path.join(save_folder, f'{f_outname}.txt'))


class SimpleShadeImagePostProcessor:
    """ Post process data to binary mask band"""

    def __init__(self, threshold=10, value=1, add_constraint_band=True, overwrite=True):

        self.threshold = threshold
        self.value = value

        self.add_constraint_band = add_constraint_band
        self.overwrite = overwrite

    def process(self, targets_path, reference):

        targets = [RasterImage.from_file(target) for target in targets_path]
        reference = RasterImage.from_file(reference)

        self.glue_geo_info(targets, reference, targets_path)

        self.threshold_bl_value(targets)
        post_processed = self.stack_image(targets)

        # need float for interpolation to work
        post_processed.data = post_processed.data.astype('float32')

        return post_processed

    def glue_geo_info(self, targets, reference, targets_path):
        meta = reference.meta
        for i, (raster, path) in enumerate(zip(targets, targets_path)):
            raster.meta = meta

            if self.overwrite:
                raster.save(path)

    def threshold_bl_value(self, target):
        """ Transform the image to black and white and apply the threshold to have value from 0 to 1"""
        for raster in target:
            raster.data = post_process_hand_cleaned(raster.data, value=self.value)

    def stack_image(self, targets):
        """ Stack the image"""
        stacked = []
        post_processed = RasterImage(None, None)
        for raster in targets:
            stacked.append(raster.data)

        _fix_overlaping_pixel(stacked)

        if self.add_constraint_band:
            stacked = _add_constraint_band(stacked)

        post_processed.data = np.array(stacked)
        post_processed.meta = targets[0].meta

        return post_processed

class SoilShadeMaskImagePostProcessor(SimpleShadeImagePostProcessor):


    def __init__(self, threshold=10, value=1, add_constraint_band=True, overwrite=True):
        super().__init__(threshold, value, add_constraint_band, overwrite)

    def process(self, targets, reference):

        assert len(targets)>1

        #run the simple image pre processor
        raster = super().process(targets[:-1], reference)
        # add the constraint band
        constraint = RasterImage.from_file(targets[-1])
        self.threshold_bl_value([constraint])
        raster.data = np.concatenate( (raster.data, [constraint.data]),axis=0 )
        return raster

def _fix_overlaping_pixel(stacked):
    """Assume that a pixel is 100% on category. Set the pixel in the following band to 0"""
    mask = np.zeros_like(stacked[0], dtype=bool)
    for b in stacked:
        b[...] = b * np.logical_not(mask)
        mask += np.logical_or(mask, b == 1)


def _add_constraint_band(stacked):
    """add a band with a value such that Sum(band)==1
    Maybe need to be done after reprojection"""
    last_b = np.ones_like(stacked[0])

    for b in stacked:
        last_b = last_b - b
    stacked.append(last_b)
    return stacked


class ShadeDatasSetCreator:
    """Create PyTorch datasets for shade/tree detection from preprocessed imagery.

    Orchestrates the full pipeline: preprocessing raw annotations, spatial alignment with
    satellite imagery, and creation of PyTorch training/validation datasets. Supports
    temporal datasets with year as additional input.

    Attributes:
        training_date (list): Years corresponding to training rasters.
        training_raster (list): Paths to processed training raster files.
        in_folder (str): Input folder containing raw annotations.
        preprocessor (DatasetPostProcessor): Handles annotation preprocessing.
        dataset_creator (ShadeMatchNNInput): Creates spatially-aligned datasets.
        with_year (bool): Whether to include year as neural network input.
        year_normalisation (int): Normalization divisor for year values.
    """

    def __init__(self,
                 in_folder: str,
                 post_process_f,
                 dataset_creator: ShadeMatchNNInput,
                 with_year: bool=False,
                 year_normalisation: int=2500):
        """Initialize ShadeDatasSetCreator.

        Args:
            in_folder (str): Input folder containing raw annotation images.
            post_process_f: Post-processing function for cleaning/transforming annotations.
            dataset_creator (ShadeMatchNNInput): Object for creating aligned datasets.
            with_year (bool, optional): Include year as NN input feature. Defaults to False.
            year_normalisation (int, optional): Divisor for normalizing year values to [0,1].
                Input becomes year/year_normalisation. Defaults to 2500.
        """


        self.training_date = None
        self.training_raster = None
        self.in_folder = in_folder
        # Pre processor to fix clean value to hand cleaned
        self.preprocessor = DatasetPostProcessor(post_process_f)
        self.dataset_creator = dataset_creator

        self.with_year = with_year
        self.year_normalisation = year_normalisation

    def prepare_dataset(self,
                        mask_raster,
                        mask_f,
                        training_folder,
                        targets=('shade.tif', 'soil.tif'),
                        reference='google.tif',
                        mode="one",
                        info='info.txt',
                        save_all=True,
                        outname="out",
                        pre_process_folder=None):
        """
        :param mask_raster: given as an input to the dataset make to further mask pixel.
        :param mask_f: used by the dataset creator to mask pixel
        :param training_folder:
        :param targets:
        :param reference:
        :param mode:
        :param info:
        :param save_all:
        :param outname:
        :param pre_process_folder:
        :return:
        """

        context = tempfile.TemporaryDirectory() if pre_process_folder is None else contextlib.nullcontext(pre_process_folder)

        with context as pre_process_dir:
            self.preprocessor.process_folder(in_folder=self.in_folder,
                                             out_folder=pre_process_dir,  # out_folder_shade
                                             targets=targets,
                                             reference=reference,
                                             mode=mode,
                                             info=info,
                                             outname=outname)

            #
            # create raster reader
            #

            self.training_raster, self.training_date = self.dataset_creator.create_nn_output(pre_process_dir,
                                                                                             training_folder,
                                                                                             mask=mask_raster,
                                                                                             mask_f=mask_f,
                                                                                             save_all=save_all)

    def nn_training_dataset(self,
                            width,
                            n_out,
                            out_function,
                            test_size=0.15,
                            validation_size=0.15,
                            transformer=None):
        ''' Given the raster reader, create the dataset the train the nn'''

        #pixel_at_band = PixelAtBandSkipValue(center_pixel, center_pixel, not_coffee)

        if self.with_year:
            dataset = BasicYearTrainingDataset(self.training_raster, self.training_date, width, 1, n_out, out_function,
                                               f_transform=transformer, year_normalisation=self.year_normalisation)
        else:
            dataset = BasicTrainingDataset(self.training_raster, width, 1, n_out, out_function, f_transform=transformer)

        #train_idx, val_idx = train_test_split(list(range(len(dataset))), test_size=test_size)

        #print([1 - test_size - validation_size, test_size, validation_size])

        train_idx, test_id, val_idx = random_split(dataset,
                                                   [1 - test_size - validation_size, test_size, validation_size])
        #print(len(train_idx), len(test_id), len(val_idx))

        return {'train': train_idx, 'test': test_id, "val": val_idx}

        #train_idx, test_id, val_idx = random_split(list(range(len(dataset))), [1 - test_size - validation_size, test_size, validation_size])
        #return {'train': Subset(dataset, train_idx), 'test': Subset(dataset, test_id), "val": Subset(dataset, val_idx)}

    def nn_per_image_dataset(self,
                            width,
                            n_out,
                            out_function,
                            transformer=None):
        ''' Return one dataset per image.'''

        if self.with_year:
            dataset = [(BasicYearTrainingDataset([raster], [date], width, 1, n_out, out_function,
                                               f_transform=transformer, year_normalisation=self.year_normalisation), raster, date)
                       for raster, date in zip (self.training_raster, self.training_date)]
        else:
            dataset = [(BasicTrainingDataset([raster], width, 1, n_out, out_function, f_transform=transformer), raster)
                       for raster in self.training_raster]

        return dataset





    def write_mask(self, mask_function, out_folder):
        ''' Map all the sample of this dataset. This can be used to map a validation dataset and compare the results'''
        for raster_path in self.training_raster:
            raster = RasterImage.from_file(raster_path)
            raster.data=  np.apply_along_axis(mask_function, 0, raster.data)

            raster.save(f"{out_folder}/{Path(raster_path).name}")