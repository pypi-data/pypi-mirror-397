"""Map dataset utilities for applying neural networks to raster imagery.

This module provides tools for iterating over raster data in a sliding window fashion,
applying neural network predictions, and aggregating results back to raster format.
Supports parallel processing and various optimization strategies.
"""

import copy
import logging
import math
from typing import Union

import numpy as np
import rasterio
import torch
import torch.multiprocessing as mp

from eoml import get_write_profile
from eoml.torch.cnn.outputs_transformer import OutputTransformer
from eoml.torch.cnn.torch_utils import align_grid
from rasterio.windows import Window
from shapely.geometry import box
from torch.utils.data import IterableDataset, DataLoader
from tqdm import tqdm

logger = logging.getLogger(__name__)

class BatchMeta:
    """Metadata for a batch of data windows.

    Attributes:
        window (Window, optional): Rasterio window specification.
        is_finished (bool): Whether this is the last batch for current window.
        worker (int): Worker ID that processed this batch.
    """

    def __init__(self, window: Union[Window, None], is_finished: bool, worker: int):
        """Initialize BatchMeta.

        Args:
            window (Window, optional): Rasterio window for this batch.
            is_finished (bool): Whether this completes processing of current window.
            worker (int): Worker ID that processed this batch.
        """
        self.window = window
        self.is_finished = is_finished
        self.worker = worker

def continuous_split(dataset, worker_id:int, n_workers: int):
    """Split dataset windows continuously across workers.

    Each worker receives adjacent contiguous blocks. Better for locality when
    overlapping cells may be cached by GDAL.

    Args:
        dataset: Dataset with target_windows attribute.
        worker_id (int): ID of current worker.
        n_workers (int): Total number of workers.

    Returns:
        list: Subset of target_windows for this worker.
    """

    size, reminder = divmod(len(dataset.target_windows), n_workers)

    if worker_id < reminder:
        size = size + 1
        start = worker_id * size
        end = start + size
        # make a deep copy to try to avoid the shared memory copy issue

    else:
        # the reminder are consumed by the previous worker
        start = worker_id * size + reminder
        end = start + size

    return dataset.target_windows[start:end]


def jumped_split(dataset, worker_id: int, n_workers: int):
    """Split dataset windows in interleaved fashion across workers.

    Workers process blocks i, i+n_workers, i+2*n_workers, etc. Better for seeing
    overall progress as work is distributed across the full spatial extent.

    Args:
        dataset: Dataset with target_windows attribute.
        worker_id (int): ID of current worker.
        n_workers (int): Total number of workers.

    Returns:
        list: Subset of target_windows for this worker (every n_workers-th window).
    """
    return dataset.target_windows[worker_id::n_workers]


def windows_in_mask(window: Window, transform, mask):
    """Check if a raster window intersects with spatial mask.

    Args:
        window (Window): Rasterio window to check.
        transform: Affine transform for the raster.
        mask: List of shapely geometries defining the mask.

    Returns:
        bool: True if window intersects any geometry in mask.
    """
    bounds = box(*rasterio.windows.bounds(window, transform))
    return any(map(lambda shape: shape.intersects(bounds), mask))

# remove soon
class IterableMapDataset(IterableDataset):
    """Iterable dataset for applying CNNs to raster imagery using sliding windows.

    Reads raster data in windows and extracts overlapping patches for CNN inference.
    Creates an aligned output raster with convolution border handling. When stride > 1,
    windows starting at top-left with size stride x stride are filled with NN output.

    Attributes:
        raster_reader: Reader for input raster data.
        size (int): Kernel/window size for CNN.
        half_size (int): Half of kernel size (for padding calculations).
        target_windows (list, optional): List of windows to process.
        off_x (float): X offset for window alignment.
        off_y (float): Y offset for window alignment.
        device (str): Device for tensor operations.
        stride (int): Stride for window extraction.
        batch_size (int): Number of samples per batch.
        worker_id (int): ID of current worker process.
    """
    # Create an aligned raster with cropped border to take the convolution into account.
    # If stride is >1, the widows starting at the top left corner and size stride X stride
    # will be filled with the value returned by the NN.

    def __init__(self, raster_reader, kernel_size, target_windows=None, off_x=None, off_y=None, stride=1, batch_size=1024,
                 device="cpu"):
        """Initialize IterableMapDataset.

        Args:
            raster_reader: RasterReader instance for input data.
            kernel_size (int): Size of CNN input window (must be odd).
            target_windows (list, optional): Pre-defined windows to process. Defaults to None.
            off_x (float, optional): X offset for alignment. Defaults to kernel_size/2.
            off_y (float, optional): Y offset for alignment. Defaults to kernel_size/2.
            stride (int, optional): Stride for window extraction. Defaults to 1.
            batch_size (int, optional): Batch size for processing. Defaults to 1024.
            device (str, optional): PyTorch device. Defaults to "cpu".

        Raises:
            Exception: If kernel_size is even (only odd kernels supported).
        """

        super().__init__()

        self.raster_reader = raster_reader

        self.size = kernel_size
        self.half_size = math.floor(kernel_size / 2)

        self.target_windows = target_windows


        if kernel_size % 2 == 0:
            raise "odd kernel not supported yet"

        if off_x is None:
            off_x = kernel_size / 2

        if off_y is None:
            off_y = kernel_size / 2

        self.off_x = off_x
        self.off_y = off_y

        self.device = device


        self.stride = stride

        # Return the list of block with corresponding target input
        # filter the list based on a shapefile if needed
        # each worker has a list of block assignated
        # load a block in memory
        # read the block nline by nline? and create input return with cell id and line id

        self.batch_size = batch_size
        self.worker_id = 0


    def __iter__(self):
        """
        iterator over the dataset. return at most batch_size data or the number of data needed to finish the current
        block of data.
        :return: data, (target_windows, is_block_finished, worker_id)
        """

        with self.raster_reader as reader:
            for ji, window in self.target_windows:

                (col_off, row_off, w_width, w_height) = window.flatten()
                # compute the source windows
                window_source = Window(col_off + self.off_x - self.half_size, row_off + self.off_y - self.half_size,
                                       w_width + self.size - 1, w_height + self.size - 1)

                a = reader.read_windows(window_source)
                buffer = torch.from_numpy(a).to(self.device)

                for tmp in self.extract_tensor_iter(buffer, self.batch_size):
                    sample, meta = tmp
                    meta.window = window
                    yield sample, meta

    def extract_tensor_iter(self, data, batch_size):
        """
        Read the nn windows from the given data
        :param data:
        :param batch_size:
        :return:
        """
        _, height, width = data.shape

        height = height - self.size + 1
        width = width - self.size + 1

        samples = []

        count = 0

        for i in range(0, height, self.stride):
            for j in range(0, width, self.stride):
                if count == batch_size:
                    yield torch.stack(samples, dim=0), BatchMeta(None, False, self.worker_id)
                    samples = []
                    count = 0
                source_w = data.narrow(1, i, self.size).narrow(2, j, self.size)
                samples.append(source_w)
                count += 1

        yield torch.stack(samples, dim=0), BatchMeta(None, True, self.worker_id)


    @staticmethod
    def basic_worker_init_fn(worker_id, splitting_f=jumped_split):
        """
        A basic function splitting the worker job to the dataset. Try to make deep copy where needed to avoid the
        memory issue when multiple worker (test needed)
        :param worker_id:
        :param splitting_f:
        :return:
        """
        worker_info = torch.utils.data.get_worker_info()

        dataset = worker_info.dataset  # the dataset copy in this worker process
        n_workers = worker_info.num_workers

        # make a deep copy to try to avoid the shared memory copy issue
        dataset.target_windows = copy.deepcopy(splitting_f(dataset, worker_id, n_workers))
        dataset.worker_id = worker_id

        # make a copy of the dataset_reader for thread safety
        dataset.raster_reader = copy.copy(dataset.raster_reader)

class IterableYearMapDataset(IterableMapDataset):
    def __init__(self, raster_reader, year, kernel_size, target_windows=None, off_x=None, off_y=None, stride=1, batch_size=1024,
                 device="cpu", year_normalisation=2500):
        super().__init__(raster_reader, kernel_size, target_windows, off_x, off_y, stride, batch_size, device)

        self.year = year
        self.year_normalisation=year_normalisation
        logger.info("initialize IterableYearMapDataset")
    def extract_tensor_iter(self, data, batch_size):
        """
        Read the nn windows from the given data
        :param data:
        :param batch_size:
        :return:
        """
        _, height, width = data.shape

        height = height - self.size + 1
        width = width - self.size + 1

        samples = []

        count = 0

        for i in range(0, height, self.stride):
            for j in range(0, width, self.stride):
                if count == batch_size:
                    yield (torch.stack(samples, dim=0), np.array([[self.year/self.year_normalisation]
                                                                  for _ in range(len(samples))],dtype=np.float32)),\
                        BatchMeta(None, False, self.worker_id)
                    
                    samples = []
                    count = 0
                source_w = data.narrow(1, i, self.size).narrow(2, j, self.size)
                samples.append(source_w)
                count += 1

        yield (torch.stack(samples, dim=0), np.array([[self.year/self.year_normalisation] for _ in range(len(samples))],
                                                     dtype=np.float32),), BatchMeta(None, True, self.worker_id)

class MapResultAggregator:
    """
    Recieve the result back from the processing and write it ot a map
    TODO manage encoder decoder
    """

    def __init__(self, path_out, output_transformer: OutputTransformer, n_windows, write_profile):

        self.bands = output_transformer.bands
        self.write_profile = copy.deepcopy(write_profile)
        self.write_profile.update({"dtype": output_transformer.dtype,
                                   "count": output_transformer.bands})
        self.result_cache = {}

        self.path_out = path_out
        self.output_transformer = output_transformer
        self.n_windows = n_windows

    def submit_result(self, values, meta: BatchMeta):

        values = self.output_transformer(values)
        # values = values.reshape((self.n_band,windows.width, windows.height))
        cached = self.result_cache.setdefault(meta.worker, [])

        cached.append(values)

        if meta.is_finished:
            values = self.reshape(cached, meta.window)
            cached.clear()
            self.write(values, meta.window)

    def reshape(self, data, windows):
        """
        Take a list of n array of abritraty length and n_bands depth and return a windows of size n_chanel, height, width
        :param data:
        :param windows:
        :return:
        """
        #out = np.empty((self.n_bands, windows.height, windows.width), dtype=self.d_type)

        width = windows.width
        height = windows.height
        #concatenate make one array. then we reshape and move the band which is in the last position to the first
        return np.moveaxis(np.concatenate(data).reshape((height, width, self.bands)), 2, 0)

    def write(self, data, windows):
        """
        todo currently flush after each windows maybe perf cost
        :param data:
        :param windows:
        :return:
        """
        # for some reason if not in threading spawn mode, setting any other option cause a deadlock num_threads=4
        with rasterio.open(self.path_out, "r+", sharing=False ) as writer:
            writer.write(data, window=windows)


class AsyncAggregator(mp.Process):
    """
    wrapper around an aggregator which does the operation asynchronously
    """
    def __init__(self, aggregator: MapResultAggregator, max_queue=5):
        super().__init__(daemon=True)
        self.queue = mp.Queue(max_queue)
        self.aggregator = copy.deepcopy(aggregator)
        self.windows_left = aggregator.n_windows

        self.daemon = True

    def run(self):
        while True:
            data, meta = self.queue.get()
            self.aggregator.submit_result(data, meta)
            del data
            if meta.is_finished:
                self.windows_left -= 1
                if self.windows_left == 0:
                    return

    def submit_result(self, values, meta):
        self.queue.put((values, meta))


class GenericMapper:
    """ apply a generic mapping function. (allow to run random forest and co)
        use no_collate to work on numpy
    """
    def __init__(self,
                 mapper,
                 stride=1,
                 loader_device='cpu',
                 mapper_device='cpu',
                 pin_memory=False,
                 num_worker=0,
                 prefetch_factor=2,
                 custom_collate=None,
                 worker_init_fn=None,
                 aggregator=MapResultAggregator,
                 write_profile=None,
                 async_agr=True):

        logger.info("setting model to eval mode")


        self.mapper = mapper.to(mapper_device)
        self.mapper.eval()
        self.stride = stride

        self.loader_device = loader_device
        self.mapper_device = mapper_device
        self.pin_memory = pin_memory
        self.num_worker = num_worker
        self.prefetch_factor = prefetch_factor

        self.custom_collate = custom_collate

        self.worker_init_fn = worker_init_fn

        if num_worker > 0 and worker_init_fn is None:
            raise Exception("A custom worker_init_fn is needed for map iterator when parallel mode is used")

        # factory should be used instead but for now
        self.aggregator = aggregator
        self.async_agr = async_agr

        self.write_profile = write_profile

    def map(self,
            out_path,
            map_iterator,
            output_transformer: OutputTransformer,
            bounds=None,
            mask=None):

        map_iterator, aggregator = self.mapping_generator(map_iterator,
                                                     out_path,
                                                     output_transformer,
                                                     bounds=bounds,
                                                     mask=mask,
                                                     write_profile=self.write_profile)

        dl = DataLoader(map_iterator, collate_fn=self.custom_collate, pin_memory=self.pin_memory,
                        num_workers=self.num_worker, prefetch_factor=self.prefetch_factor,
                        worker_init_fn=self.worker_init_fn)

        if self.async_agr:
            aggregator = AsyncAggregator(aggregator, 10)
            aggregator.start()

        with torch.inference_mode():
            with tqdm(total=len(map_iterator.target_windows), desc='Map') as pbar:

                for inputs, meta in dl:
                    # increment when windows are finished

                    # nn_inputs = inputs[0].to(device)
                    # release cuda memory as soon as possible

                    out = self.process_batch(inputs)

                    aggregator.submit_result(out, meta[0])

                    if meta[0].is_finished:
                        # to monitor cuda
                        # if nn_device == "cuda":
                        #    pbar.set_postfix({'allocated': torch.cuda.memory_allocated(),
                        #                      'max allocated': torch.cuda.max_memory_allocated(),
                        #                      'reserved': torch.cuda.memory_reserved(),
                        #                      'max reserved': torch.cuda.max_memory_reserved()}, refresh=False)
                        pbar.update(1)

        if self.async_agr:
            aggregator.join()

    def process_batch(self, inputs):

        if isinstance(inputs, (list, tuple)):
            inputs = map(lambda x: x.to(self.mapper_device, non_blocking=True), inputs)
        else:
            inputs = inputs.to(self.mapper_device, non_blocking=True)

        # if not traced we need to run pass  to the function *inputs
        outputs = self.mapper(*inputs)
        del inputs
        s = outputs.detach().cpu().numpy()
        del outputs
        return s



    def mapping_generator(self,
                          map_iterator,
                          path_out,
                          output_transformer: OutputTransformer,
                          bounds=None,
                          mask=None,
                          write_profile=None):
        """
        Generate a mapiterator and a agregattor to be used for mapping
        :param map_iterator:
        :param output_transformer:
        :param path_out:
        :param kernel_size:
        :param bounds:
        :param mask:
        :param write_profile:
        :return:
        """
        # TODO adapt the code for when windows are not block and to take into account encoder decoder

        ref_raster = map_iterator.raster_reader.ref_raster()

        with rasterio.open(ref_raster, mode="r") as raster_source:
            src = raster_source

        if write_profile is None:
            write_profile = get_write_profile()

        if map_iterator.size % 2 == 0:
            raise "odd kernel not supported yet"

        if not bounds:
            bounds = src.bounds

        # this function i based on the center pixel need adjustement for fully convolutional
        transform, width, height, off_x, off_y = align_grid(src.transform, bounds, src.width, src.height, map_iterator.size)

        write_profile.update({'dtype': output_transformer.dtype,
                              'crs': src.crs,
                              'transform': transform,
                              'width': width,
                              'height': height,
                              'nodata': output_transformer.nodata,
                              'count': output_transformer.bands})
        # out_profile =out_meta(src.meta, 5, 1)
        # create an empty raster
        with rasterio.open(path_out, mode="w", **write_profile) as dst:
            windows = list(dst.block_windows())

        if mask is not None:
            windows = list(filter(lambda x: windows_in_mask(x[1], transform, mask), windows))

        # set the good parameter to the map iterator
        map_iterator.target_windows = windows
        map_iterator.off_x = off_x
        map_iterator.off_y = off_y


        aggregator = self.aggregator(path_out, output_transformer, len(windows), write_profile)

        return map_iterator, aggregator


class NNMapper(GenericMapper):
    """
    Object specialised to run nn
    """
    def __init__(self,
                 model,
                 stride=1,
                 loader_device='cpu',
                 mapper_device='cpu',
                 pin_memory=False,
                 num_worker=0,
                 prefetch_factor=2,
                 custom_collate=None,
                 worker_init_fn=None,
                 aggregator=MapResultAggregator,
                 write_profile=None,
                 async_agr=True):

        super().__init__(model, stride, loader_device, mapper_device, pin_memory, num_worker,
                         prefetch_factor, custom_collate, worker_init_fn, aggregator, write_profile, async_agr)




