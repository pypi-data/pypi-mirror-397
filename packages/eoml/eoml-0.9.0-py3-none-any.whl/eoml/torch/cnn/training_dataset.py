"""PyTorch datasets for training from raster images.

Provides dataset classes that extract training samples from raster images by sliding
windows. Includes support for data augmentation, temporal features (year), and
multi-band output processing.
"""

import itertools

import numpy as np
import torch
from libterra_gis.raster_utils import RasterImage
from eoml.torch.cnn.augmentation import rotate_flip_transform
from torch.utils.data import Dataset


class BasicTrainingDataset(Dataset):
    """Training dataset that extracts windows from raster images.

    Loads raster images, extracts overlapping windows using stride, and stores all
    samples in memory. Applies output function to determine sample validity.
    Currently used for shade generation tasks.

    Attributes:
        f_transform: Data augmentation function.
        transform_param (np.ndarray, optional): Per-sample augmentation parameters.
        paths (list): Paths to input raster files.
        size (int): Window size for extraction.
        func: Function to process output windows and determine validity.
        stride (int): Stride for window extraction.
        n_out (int): Number of output bands.
        samples (list): List of (input, output) sample tuples.
    """
    def __init__(self, paths, size, stride, n_out, func, f_transform=None, transform_param=None):
        """Initialize BasicTrainingDataset.

        Args:
            paths (list): List of paths to raster image files.
            size (int): Size of windows to extract.
            stride (int): Stride between consecutive windows.
            n_out (int): Number of output bands (taken from last bands of raster).
            func: Function applied to output windows. Returns None for invalid samples.
            f_transform (callable, optional): Data augmentation function. Defaults to None.
            transform_param (list, optional): Per-sample transform parameters. Defaults to None.
        """

        self.f_transform = f_transform

        if transform_param is not None:
            self.transform_param = np.array(transform_param)
        else:
            self.transform_param = transform_param

        self.paths = paths
        self.size = size
        self.func = func
        self.stride = stride
        self.n_out = n_out

        self.samples = self.extract()

    def extract(self):

        samples = []

        for path in self.paths:
            data = RasterImage.from_file(path).data

            bands, height, width = data.shape

            # print(data.shape)
            # nh = math.floor((height-self.size)/self.stride+1)
            # nw = math.floor((width-self.size)/self.stride+1)

            for i in range(0, height - self.size + 1, self.stride):
                for j in range(0, width - self.size + 1, self.stride):
                    source_w = data[:-self.n_out, i:i + self.size, j:j + self.size]
                    output_w = data[-self.n_out:, i:i + self.size, j:j + self.size]
                    output_w = self.func(output_w)

                    if output_w is not None:
                        samples.append((source_w, output_w))

        return samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):

        if hasattr(idx, '__iter__'):
            return self._get_items(idx)

        if isinstance(idx, int):
            return self._get_one_item(idx)

        if isinstance(idx, slice):
            # Get the start, stop, and step from the slice
            return self._get_items(range(idx.start, idx.stop, idx.step))

    def _get_items(self, iterable):

        labels = []

        batch = len(iterable)
        iterable = iterable.__iter__()
        try:
            (one_input,), target = self._get_one_item(next(iterable))
        except StopIteration:
            return []

        # compute the shape
        shape_out = (batch,) + one_input.shape
        datas =  torch.empty(shape_out, dtype=torch.long)

        if isinstance(target, int):
            shape_out = batch
            labels = torch.empty(shape_out, dtype=torch.long)
        else:
            shape_out = (batch,) + target.shape
            labels = torch.empty(shape_out, dtype=torch.float32)

        datas[0] = one_input
        labels[0] = target

        for i, key in enumerate(iterable, 1):
            # the nn take on parameter so we unpack the 1 tuples and make it for the batch
            (datas[i],), labels[i] = self._get_one_item(key)
        # the nn take on parameter so we make a 1 element tuple
        return (datas,), labels


    def _get_one_item(self, idx):
        inputs, output = self.samples[idx]

        inputs = torch.from_numpy(inputs)
        output = torch.from_numpy(output)

        if self.f_transform is not None:
            if self.transform_param is not None:
                inputs = self.f_transform(inputs, *self.transform_param[idx])
            else:
                inputs = self.f_transform(inputs)

        return (inputs,), output

    def add_rotation_flip(self):
        self.f_transform = rotate_flip_transform
        self.samples, self.transform_param = self._augmentation_setup(self.samples, [0, 90, 180, 270], [False, True])

    def _augmentation_setup(self, samples, angles=None, flip=None):

        if angles is None:
            angles = [0, 90, 180, -90]

        if flip is None:
            flip = [False, True]

        t_param_list = list(itertools.product(angles, flip))

        t_params = []
        samples_split = []
        for k in samples:
            for p in t_param_list:
                t_params.append(p)
                samples_split.append(k)

        return samples_split, t_params



class BasicYearTrainingDataset(BasicTrainingDataset):
    """Training dataset with year as additional input feature.

    Extends BasicTrainingDataset to include temporal information (year) as an additional
    input alongside image patches. Year values are normalized for neural network input.

    Attributes:
        years (list): Year values corresponding to each raster image.
        year_normalisation (int): Value used to normalize years (year/year_normalisation).
    """

    def __init__(self, paths, years, size, stride, n_out, func, f_transform=None, transform_param=None, year_normalisation=2050):
        """Initialize BasicYearTrainingDataset.

        Args:
            paths (list): List of paths to raster image files.
            years (list): Year value for each raster file.
            size (int): Size of windows to extract.
            stride (int): Stride between consecutive windows.
            n_out (int): Number of output bands.
            func: Function applied to output windows. Returns None for invalid samples.
            f_transform (callable, optional): Data augmentation function. Defaults to None.
            transform_param (list, optional): Per-sample transform parameters. Defaults to None.
            year_normalisation (int, optional): Normalization divisor for year values.
                Defaults to 2050.
        """
        self.years = years
        self.year_normalisation = year_normalisation
        super().__init__(paths, size, stride, n_out, func, f_transform, transform_param)


    def extract(self):

        samples = []

        for path, year in zip(self.paths, self.years):
            data = RasterImage.from_file(path).data

            bands, height, width = data.shape

            # print(data.shape)
            # nh = math.floor((height-self.size)/self.stride+1)
            # nw = math.floor((width-self.size)/self.stride+1)

            for i in range(0, height - self.size + 1, self.stride):
                for j in range(0, width - self.size + 1, self.stride):
                    source_w = data[:-self.n_out, i:i + self.size, j:j + self.size]
                    output_w = data[-self.n_out:, i:i + self.size, j:j + self.size]
                    output_w = self.func(output_w)

                    if output_w is not None:
                        samples.append((source_w,  np.array([year/self.year_normalisation], dtype= np.float32), output_w))

        return samples

    def _get_one_item(self, idx):
        inputs, year, output = self.samples[idx]

        inputs = torch.from_numpy(inputs)
        output = torch.from_numpy(output)

        if self.f_transform is not None:
            if self.transform_param is not None:
                inputs = self.f_transform(inputs, *self.transform_param[idx])
            else:
                inputs = self.f_transform(inputs)

        return inputs, year, output


