"""Raster data extraction module for creating labeled datasets.

This module provides classes for extracting windows of raster data around labeled
point locations. It supports various optimization strategies including block-level
reading, parallel processing with threads or processes, and efficient I/O operations.

The extractors are designed to work with geospatial vector files (containing labeled
points) and raster files, producing datasets suitable for machine learning training.
"""

import copy
import logging
import math
import threading
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Process, Queue
from typing import List, Union

logger = logging.getLogger(__name__)

import fiona
import numpy as np
import rasterio
import rasterio.crs
import rasterio.warp
import shapely
from eoml.data.basic_geo_data import GeoDataHeader, BasicGeoData
from eoml.data.persistence.generic import GeoDataWriter
from eoml.data.persistence.lmdb import LMDBWriter
from eoml.raster.raster_reader import RasterReader, AbstractRasterReader
from rasterio.windows import Window
from rasterio.windows import round_window_to_full_blocks
from shapely.geometry import shape
from tqdm import tqdm


class Header:
    """Container for sample metadata during extraction.

    Attributes:
        label: Class label for the sample.
        geometry: Shapely geometry (typically Point) for the sample location.
        idx: Unique identifier for the sample.
        window: Rasterio window defining the extraction area.
    """
    def __init__(self, label, geometry, idx=None):
        self.label = label
        self.geometry = geometry
        self.idx = idx
        self.window: Window | None = None

#row col
#header.y, header.x

class AbstractExtractor:
    """Abstract base class for dataset extractors.

    Defines the interface for extracting labeled windows from raster data.
    """

    @abstractmethod
    def _prepare(self):
        """Prepare headers and metadata for extraction.

        Returns:
            List of Header objects ready for extraction.
        """
        ...

    @abstractmethod
    def _extract(self, headers: List[Header]):
        """Extract data for the given headers.

        Args:
            headers: List of Header objects defining what to extract.
        """
        ...


    @abstractmethod
    def process(self):
        """Execute the complete extraction workflow."""
        ...


def basic_extract_iter(samples: List[Header], location, reader):
    """Generate extracted samples by reading each window individually.

    Args:
        samples: List of headers defining extraction windows.
        location: Path to a vector file with sample locations.
        reader: Raster reader instance.

    Yields:
        BasicGeoData: Extracted raster data with metadata and label.
    """
    for header in samples:
        data = reader.read_windows(header.window)

        if LabeledWindowsExtractor.is_valid(data):
            yield BasicGeoData(GeoDataHeader(header.idx, header.geometry, location), data, header.label)


def extract_blocks_iter(h_list, window_tuple, location, reader):
    """Generate extracted samples from a single large block read.

    More efficient than individual reads when multiple samples are close together.

    Args:
        h_list: List of headers within the block.
        window_tuple: Tuple defining the block window (col_off, row_off, width, height).
        location: Path to a vector file with sample locations.
        reader: Raster reader instance.

    Yields:
        BasicGeoData: Extracted raster data with metadata and label.
    """
    window = Window(*window_tuple)

    # Data array to read from
    data = reader.read_windows(window)

    for i, h in enumerate(h_list):
        row, col = OptimiseLabeledWindowsExtractor._slice_to_read(h.window, window)
        data_h = data[:, row, col]

        if LabeledWindowsExtractor.is_valid(data_h):
            yield BasicGeoData(GeoDataHeader(h.idx, h.geometry, location), data_h, h.label)

class LabeledWindowsExtractor(AbstractExtractor):
    """Extract labeled windows from raster data around point locations.

    Reads windows of specified size centered on labeled point locations from
    vector data. Uses floor operation for pixel indexing, ensuring the pixel
    containing the point is extracted.

    Todo:
        Save all metadata as a dictionary.

    Attributes:
        locations: Path to vector file with labeled points.
        writer: GeoDataWriter for saving extracted samples.
        raster_reader: Reader for the raster data.
        windows_size: Size of extraction windows in pixels.
        labelName: Name of the label field in vector data.
        id_field: Name of the ID field in vector data.
        geometryName: Name of the geometry field.
        locationsCRS: Coordinate system of the location data.
        rasterCRS: Coordinate system of the raster data.
        show_progress: Whether to display progress bars.
        mask: Optional geometry to filter extraction locations.
    """
    def __init__(self,
                 locations: str,
                 writer: Union[GeoDataWriter, None],
                 raster_reader: RasterReader,
                 windows_size: int,
                 label_name: str = 'class',
                 id_field: str = None,
                 geometry_name: str = 'geometry',
                 mask_path: str = None,
                 show_progress: bool = True):

        self.locations = locations

        self.writer: GeoDataWriter = writer

        self.raster_reader: AbstractRasterReader = raster_reader
        self.windows_size: int = windows_size
        self.labelName: str = label_name
        self.id_field: str = id_field
        self.geometryName: str = geometry_name

        with fiona.open(self.locations) as locs:
            self.locationsCRS = rasterio.crs.CRS.from_dict(locs.crs)

        with rasterio.open(self.raster_reader.ref_raster()) as src:
            self.rasterCRS = src.crs

        self.show_progress = show_progress

        self.mask = None

        if mask_path is not None:
            with fiona.open(mask_path) as mask:
                self.mask = shapely.geometry.MultiPolygon([shape(feature[self.geometryName]) for feature in mask])


    def _prepare(self):

        headers = self._read_header(self.locations)
        self._reproject(headers)
        self._read_location(headers)

        if self.mask is not None:
            headers = self._filter_in_mask(headers)

        return self._filter_in_raster(headers)

    def _extract(self, samples, show_progress=True):
        # if only one header arrive wrap it in a list
        # can be used more easily by subclass
        if not isinstance(samples, list):
            samples = [samples]

        num = len(samples)

        # sort x and y if x equal may speed up du to cache
        samples.sort(key=lambda h: (h.col, h.row))

        with self.raster_reader as reader, self.writer as dst:
            for sample in tqdm(basic_extract_iter(samples, self.locations, reader), total=num, disable=not show_progress):
                dst.save(sample)


    def process(self):
        headers = self._prepare()
        self._extract(headers, self.show_progress)

    def _read_header(self, locations)->List[Header]:
        with fiona.open(locations) as locs:

            headers =[]
            for i, feature in enumerate(locs):
                label = feature['properties'][self.labelName]
                geometry = shape(feature[self.geometryName])
                idx = feature['properties'][self.id_field] if self.id_field is not None else i

                headers.append(Header(label, geometry, idx))

            return headers

    def _reproject(self, headers):
        # transform geom to match raster
        if self.rasterCRS != self.locationsCRS:
            geom = rasterio.warp.transform_geom(self.locationsCRS, self.rasterCRS, [h.geometry for h in headers])
            for h, geo in zip(headers, geom):
                h.geometry = shape(geo)

    def _read_location(self, headers: List[Header]):
        # loop over the feature to get coordinate
        for header in headers:
            # the methode return row column -> must invert (not the case for window
            header.window = self.raster_reader.windows_for_center(header.geometry.x,
                                                                    header.geometry.y,
                                                                    self.windows_size,
                                                                    op=math.floor)


    def _filter_in_mask(self, headers):
        return list(filter(lambda h: self.mask.contains(h.geometry), headers))

    def _filter_in_raster(self, headers: List[Header]):
        return list(filter(lambda h: self.raster_reader.is_inside(h.window), headers))


    @staticmethod
    def is_valid(data) -> bool:
        return not np.isnan(data).any()


class OptimiseLabeledWindowsExtractor(LabeledWindowsExtractor):
    """
    Extract the data window of the given size around pixel point
    """
    def __init__(self,
                 locations: str,
                 writer: GeoDataWriter,
                 raster_reader: RasterReader,
                 windows_size: int,
                 label_name: str = 'class',
                 geometry_name: str = 'geometry',
                 mask_path: str = None,
                 show_progress: bool = True):
        super().__init__(locations, writer, raster_reader, windows_size, label_name, geometry_name,
                         mask_path=mask_path,show_progress=show_progress)

        self.to_write = -1

    def _prepare(self):

        header = super()._prepare()
        self.to_write = len(header)
        windows = self._list_windows(header)
        self._merge_windows(windows)
        return windows

    def _extract(self, w_to_load, show_progress=True):
        # extract
        self._load_and_save(w_to_load, self.to_write, show_progress)

    @staticmethod
    def _slice_to_read(target: Window, src: Window):

        # based on rasterio toslices
        row_off = target.row_off - src.row_off
        col_off = target.col_off - src.col_off

        range_w = ((row_off, row_off + target.height),
                  (col_off, col_off + target.width))

        return tuple(slice(*rng) for rng in range_w)

    def _load_and_save(self, window_header_map, total, show_progress):
        """Merge the windows as 1 big windows and load the data inside
        Keyword arguments:
        """
        with self.raster_reader as reader, self.writer as writer:
            with tqdm(total=total, disable= not show_progress) as pbar:
                for window_tuple, h_list in window_header_map.items():

                    # quick test seems to show that loading 1 by one is faster on ssd when there are 5 samples or
                    # fewer in the block. More test needed for the good valye
                    if len(h_list)<5:
                        itera = basic_extract_iter(h_list, self.locations, reader)
                    else:
                        itera =  extract_blocks_iter(h_list, window_tuple, self.locations, reader)
                    for sample in itera:
                        writer.save(sample)
                        pbar.update(1)



    def _list_windows(self, headers):

        ref = self.raster_reader.ref_raster()

        with rasterio.open(ref) as src:
            block_shapes = src.block_shapes

        w_to_load = {}
        for h in headers:

            block = round_window_to_full_blocks(h.window, block_shapes)
            block = (block.col_off, block.row_off, block.width, block.height)

            list_h = w_to_load.get(block, [])
            list_h.append(h)

            w_to_load[block] = list_h

        return w_to_load

    def _merge_windows(self, windows):
        # list of (block, sample)
        k1s = windows.copy()

        for w1, l1 in k1s.items():
            # we check each element against the original dic. If one block is contained in the other, we merge it
            # inside the other and remnove the key from the list. then we iterate on the next element, on the merged
            #list
            for w2, l2 in windows.items():
                if w1 != w2 and OptimiseLabeledWindowsExtractor.windows_is_inside(*w1, *w2):
                    l2.extend(l1)
                    # we merged so we remove from the dictionnary
                    del windows[w1]
                    # we can exit the loop
                    break

    @staticmethod
    def windows_is_inside(col_off_1, row_off_1, width_1, height_1, col_off_2, row_off_2, width_2, height_2):
        """check if w1 is inside w2"""

        #(if right2 <= right1
        # and left2 >= left1
        # and top2 >= top1
        # and bottom2 <= bottom1)
        return (col_off_1 + width_1) <= (col_off_2 + width_2) and (col_off_1 >= col_off_2) and \
               (row_off_1 + height_1) <= (row_off_2 + height_2) and (row_off_1 >= row_off_2)


class AsyncKernelWriter(Process):
    """write up to max_queue kernel asynchronously"""
    def __init__(self, db_writer, n_reader, max_queue=100):
        super().__init__(daemon=True)
        self.queue = Queue(max_queue)
        self.db_writer: LMDBWriter = db_writer
        self.n_reader = n_reader
    def run(self):
        with self.db_writer:
            while True:
                window = self.queue.get()
                if window is not None:
                    self.db_writer.save(window)

                if window is None:
                    self.n_reader -= 1
                    if self.n_reader == 0:
                        return

    def submit(self, kernel):
        self.queue.put(kernel)

class AbstractPooledWindowsExtractor(OptimiseLabeledWindowsExtractor):
    def __init__(self,
                 locations: str,
                 writer: GeoDataWriter,
                 raster_reader: RasterReader,
                 windows_size: int,
                 label_name: str = 'class',
                 geometry_name: str = 'geometry',
                 mask_path: str = None,
                 show_progress: bool = True,
                 worker=4,
                 prefetch=3):
        super().__init__(locations, writer, raster_reader, windows_size, label_name, geometry_name,
                         mask_path=mask_path, show_progress=show_progress)

        self.worker = worker
        # self.reader_lock = threading.Lock()
        self.writer = AsyncKernelWriter(writer, 1)
        # we use semaphore from threading as they are thread internal
        # the number is the max number of simultaneous cell processed
        self.semaphore = threading.Semaphore(worker*prefetch)
        self.pbar =None

    def save_callback(self, future):
        # release the semaphore to allow a new task
        try:
            result = future.result()
        except Exception as e:
            logger.error(f"Extractor failed: {e}")
            raise

        for sample in result:
            self.writer.submit(sample)
            self.pbar.update(1)

        self.semaphore.release()

    def submit_proxy(self, executor, function, *args, **kwargs):
        # acquire the semaphore, blocks if occupied
        self.semaphore.acquire()
        # submit the task normally
        future = executor.submit(function, *args, **kwargs)
        # add the custom done callback
        future.add_done_callback(self.save_callback)
        return future

def init_pool(raster_r):
    """function to extract windows in the process pool"""
    # Initialize pool processes global variables:
    global glob_raster_reader
    glob_raster_reader = copy.deepcopy(raster_r)

# proxy for submitting tasks that imposes a limit on the queue size


def extract_many(h_list, window_tuple, location, raster_reader, read_lock=None):
    """Since we can not pickle generator we can not use the iterator in the process pool (copy past code here)"""
    result = []
    window = Window(*window_tuple)

    # Data array to read from
    if read_lock is not None:
        with read_lock:
            data = raster_reader.read_windows(window)
    else:
        data = raster_reader.read_windows(window)

    for i, h in enumerate(h_list):
        row, col = OptimiseLabeledWindowsExtractor._slice_to_read(h.window, window)
        data_h = data[:, row, col]

        if LabeledWindowsExtractor.is_valid(data_h):
            result.append(BasicGeoData(GeoDataHeader(h.idx, h.geometry, location), data_h, h.label))
    return result

def extract_many_pool(h_list, window_tuple, location):
    with glob_raster_reader:
        return extract_many(h_list, window_tuple, location, glob_raster_reader)

def extract_few(samples, location, raster_reader, read_lock=None):
    """Since we can not pickle generator we can not use the iterator in the process pool (copy past code here)"""
    results = []
    for header in samples:
        if read_lock is not None:
            with read_lock:
                data = raster_reader.read_windows(header.window)
        else:
            data = raster_reader.read_windows(header.window)

        if LabeledWindowsExtractor.is_valid(data):
            results.append(BasicGeoData(GeoDataHeader(header.idx, header.geometry, location), data, header.label))
    return results

def extract_few_pool(samples, location):
    with glob_raster_reader:
        return extract_few(samples, location, glob_raster_reader)


class ProcessOptimiseLabeledWindowsExtractor(AbstractPooledWindowsExtractor):
    """
    Extract the data window of the given size around pixel point. Use the optimized writing way. Is baked by a pool of
    n process worker.
     The sample are writen asynchronously to the db/

    the executor is based on https://superfastpython.com/threadpoolexecutor-limit-pending-tasks/ to limite the number
    of task. can try also with a thread pool. Possible similar perf with less complexity
    """
    def __init__(self,
                 locations: str,
                 writer: GeoDataWriter,
                 raster_reader: RasterReader,
                 windows_size: int,
                 label_name: str = 'class',
                 geometry_name: str = 'geometry',
                 mask_path: str = None,
                 show_progress: bool = True,
                 worker=4,
                 prefetch=3):
        super().__init__(locations, writer, raster_reader, windows_size, label_name, geometry_name, worker=worker,
                         prefetch=prefetch, mask_path=mask_path, show_progress=show_progress)


    def _load_and_save(self, window_header_map, total, show_progress):
        """Merge the windows as 1 big windows and load the data inside
        Keyword arguments:
        """

        self.writer.start()
        self.pbar = tqdm(total=total, disable=not show_progress)

        with ProcessPoolExecutor(max_workers=self.worker, initializer=init_pool, initargs=(self.raster_reader,))\
                as executor:
            for window_tuple, h_list in window_header_map.items():
                if len(h_list) < 5:
                    self.submit_proxy(executor,
                                      extract_few_pool,
                                      h_list,
                                      self.locations)
                else:
                    self.submit_proxy(executor,
                                      extract_many_pool,
                                      h_list,
                                      window_tuple,
                                      self.locations)
                    # normally conserve the order. This may cost more memory

            # older version of python don't have the good shutdown version
            # for f in as_completed(futures):
            #    pass
            #executor.shutdown(wait=True, cancel_futures=False)

        #send the poison pill
        self.writer.submit(None)
        self.writer.join()
        self.pbar.close()


class ThreadedOptimiseLabeledWindowsExtractor(AbstractPooledWindowsExtractor):
    """
    Extract the data window of the given size around pixel point. Use the optimized writing way. Is baked by a pool of
    n thread worker. Threading improve performance because rasterio release the GIL.
     The sample are writen asynchronously to the db/

    the executor is based on https://superfastpython.com/threadpoolexecutor-limit-pending-tasks/ to limite the number
    of task. can try also with a thread pool. Possible similar perf with less complexity
    """

    def __init__(self,
                 locations: str,
                 writer: GeoDataWriter,
                 raster_reader: RasterReader,
                 windows_size: int,
                 label_name: str = 'class',
                 geometry_name: str = 'geometry',
                 mask_path: str = None,
                 show_progress: bool = True,
                 worker=4,
                 prefetch=3):
        super().__init__(locations, writer, raster_reader, windows_size, label_name, geometry_name,
                         mask_path=mask_path, show_progress=show_progress, worker=worker, prefetch=prefetch)

        self.reader_lock = threading.Lock()

    def _load_and_save(self, window_header_map, total, show_progress):
        """Merge the windows as 1 big windows and load the data inside
        Keyword arguments:
        """

        self.writer.start()
        self.pbar = tqdm(total=total, disable=not show_progress)

        # need to be called before the pool to make sur we close the reader after the pool is done executing
        with self.raster_reader:
            with ThreadPoolExecutor(max_workers=self.worker) as executor:
                for window_tuple, h_list in window_header_map.items():
                    if len(h_list) < 5:
                        self.submit_proxy(executor, extract_few, h_list, self.locations, self.raster_reader, self.reader_lock)
                    else:
                        self.submit_proxy(executor, extract_many, h_list, window_tuple, self.locations, self.raster_reader, self.reader_lock)

                #for f in as_completed(futures):
                #    pass
                #executor.shutdown(wait=True, cancel_futures=False)

        # send the poison pill
        self.writer.submit(None)
        self.writer.join()
        self.pbar.close()


