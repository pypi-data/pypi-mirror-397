"""Raster reader module for geospatial raster data access.

This module provides wrapper classes around rasterio for reading and processing
geotiff raster data. It supports reading single rasters and multiple aligned
rasters with different resolutions and coordinate systems.

The readers are designed to be thread-safe when properly configured and support
various operations like windowed reading, coordinate-based extraction, and
on-the-fly resampling.
"""

import copy
import math
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

import numpy
import rasterio
from rasterio.transform import TransformMethodsMixin
from rasterio.windows import Window, WindowMethodsMixin

from eoml import get_read_profile
from eoml.raster.band import Band

from rasterio.enums import Resampling

from eoml.raster.raster_utils import RasterInfo


def append_raster_reader(r_list,
                         reference_index: int = 0,
                         read_profile=None,
                         sharing=False):
    """Combine multiple raster readers into a single MultiRasterReader.

    Args:
        r_list: List of RasterReader or MultiRasterReader objects to combine.
        reference_index: Index of the reader to use as spatial reference. Defaults to 0.
        read_profile: Rasterio read profile configuration. Defaults to None.
        sharing: Whether to enable file sharing mode. Defaults to False.

    Returns:
        MultiRasterReader: Combined reader for all input rasters.
    """

    paths = []
    bands = []
    transformer = []
    interpolation = []

    for r in r_list:

        if isinstance(r, RasterReader):
            paths.append(r.path)
            bands.append(r.bands_list)
            transformer.append(r.transformer)
            interpolation.append(r.interpolation)

        else:
            paths.extend(r.path)
            bands.extend(r.bands_list)
            transformer.extend(r.transformer)
            interpolation.extend(r.interpolation)

    return MultiRasterReader(paths, bands, transformer, interpolation, reference_index, read_profile, sharing)


class AbstractRasterReader(ABC):
    """Abstract base class for raster readers.

    Provides common interface for reading geotiff rasters with support for
    band selection, transformation, and various read operations.

    Warning:
        This class should either be thread-safe or properly copied for parallel mapping.

    Attributes:
        bands_list: Band selection configuration.
        transformer: Function to apply to read data.
        interpolation: Resampling method for reading.
        read_profile: Rasterio read configuration.
        path: Path to raster file(s).
        sharing: Whether file sharing is enabled.
        src_info: Raster metadata information.
    """

    @abstractmethod
    def __init__(self,
                 path,
                 bands_list: Band,
                 transformer,
                 interpolation=None,
                 read_profile=None,
                 sharing=False):
        """Initialize abstract raster reader.

        Args:
            path: Path to raster file.
            bands_list: Band configuration object.
            transformer: Optional function to transform read data.
            interpolation: Resampling method. Defaults to None (nearest neighbor).
            read_profile: Rasterio read profile. Defaults to None.
            sharing: Enable file sharing mode. Defaults to False.
        """
        self.bands_list = bands_list
        self.transformer = transformer

        if interpolation is None:
            interpolation = Resampling.nearest

        self.interpolation = interpolation
        self.read_profile = read_profile
        self.path = path

        self.sharing = sharing

        self.src_info = RasterInfo.from_file(path)

    def __repr__(self):
        return f"AbstractRasterReader({self.path}, {self.bands_list}, {self.transformer}, {self.sharing})"

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__init__(self.path, self.bands_list, self.transformer, self.interpolation, self.read_profile, self.sharing)

        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)

        path = copy.deepcopy(self.path)
        bands_list = copy.deepcopy(self.bands_list)
        transformer = copy.deepcopy(self.transformer)
        interpolation = copy.deepcopy(self.interpolation)
        read_profile = copy.deepcopy(self.read_profile)
        result.__init__(path, bands_list, transformer, interpolation, read_profile, self.sharing)

        return result

    @abstractmethod
    def ref_raster(self):
        pass

    @abstractmethod
    def ref_raster_info(self) -> RasterInfo:
        pass

    @abstractmethod
    def read_windows(self, source_window):
        pass
    @abstractmethod
    def read_windows_around_coordinate(self, center_x, center_y, size, op=math.floor):
        pass

    @abstractmethod
    def read_bound(self, bounds):
        pass

    def is_inside(self, windows: Window):
        """Check if a window is fully contained within the raster bounds.

        Args:
            windows: Rasterio window to check.

        Returns:
            bool: True if window is fully inside raster bounds, False otherwise.
        """
        return windows.row_off >= 0 and\
               windows.col_off >= 0 and\
               windows.col_off + windows.width <= self.ref_raster_info().width and\
               windows.row_off + windows.height <= self.ref_raster_info().height

    def windows_for_center(self, center_x, center_y, size, op=math.floor) -> Window:
        """Compute rasterio window centered on specified coordinates.

        By default uses floor operation, meaning the returned window contains
        the pixel at the specified point.

        Args:
            center_x: X coordinate (longitude/easting) of center point.
            center_y: Y coordinate (latitude/northing) of center point.
            size: Size of window in pixels (square window).
            op: Operation to apply when converting coordinates to pixels. Defaults to math.floor.

        Returns:
            Window: Rasterio window centered on the specified coordinates.
        """
        row, col = self.ref_raster_info().index(center_x, center_y, op=op)
        radius = math.floor(size / 2)

        col = col - radius
        row = row - radius

        return Window(col, row, size, size)


class RasterReader(AbstractRasterReader):
    """Single raster file reader with band selection and transformation.

    Wrapper around rasterio for reading geotiff files with support for
    band selection, data transformation, and various reading modes.

    Warning:
        This class should either be thread-safe or properly copied for parallel mapping.

    Attributes:
        path: Path to the geotiff file.
        bands_list: Band selection configuration.
        transformer: Function to transform read data.
        interpolation: Resampling method for reading.
        read_profile: Rasterio read configuration.
        n_band: Number of bands to read.
        src_info: Raster metadata information.
        sharing: Whether file sharing is enabled.
    """

    def __init__(self,
                 path: Path,
                 bands_list: Band,
                 transformer=None,
                 interpolation: Union[Resampling,  None] = None,
                 read_profile=None,
                 sharing=False):
        """Initialize single raster reader.

        Args:
            path: Path to the geotiff file.
            bands_list: Band configuration object specifying which bands to read.
            transformer: Optional function to apply to read data. Defaults to None.
            interpolation: Resampling method for reading. Defaults to None (nearest neighbor).
            read_profile: Rasterio read profile configuration. Defaults to None.
            sharing: Enable file sharing mode. Defaults to False.
        """

        self.path = path

        self.transformer = transformer

        if interpolation is None:
            interpolation = Resampling.nearest

        self.interpolation = interpolation

        if read_profile is None:
            self.read_profile = get_read_profile()
        else:
            self.read_profile = read_profile

        self.n_band = 0
        self.bands_list = bands_list

        if self.bands_list.selected is None:
            with rasterio.open(path, 'r', **self.read_profile) as reader:
                self.n_band = reader.count
        else:
            self.n_band = len(bands_list)

        self.src_info = RasterInfo.from_file(path)

        self.sharing = sharing
        # self.reader = None

    def __repr__(self):
        return f"RasterReader({self.path}, {self.bands_list}, {self.transformer}, {self.sharing})"

    def __enter__(self):
        self.reader = rasterio.open(self.path, 'r', **self.read_profile, sharing= self.sharing)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.reader.close()
        # set the reader to none as we can not copy it
        self.reader = None

    def ref_raster(self):
        """Get the path of the reference raster.

        Returns:
            str: Path to the raster file.
        """
        return self.path

    def ref_raster_info(self):
        """Get metadata information of the reference raster.

        Returns:
            RasterInfo: Raster metadata including CRS, transform, dimensions.
        """
        return self.src_info

    def read_windows(self, source_window):
        """Read data from a specific window of the raster.

        Args:
            source_window: Rasterio window defining the area to read.

        Returns:
            numpy.ndarray: Raster data for the specified window, optionally transformed.
        """
        if self.bands_list.selected1 is not None:
            data = self.reader.read(self.bands_list.selected1, window=source_window, boundless=True)
        else:
            data = self.reader.read(window=source_window, boundless=True)

        if self.transformer is not None:
            self.transformer(data)

        return data

    def read_windows_around_coordinate(self, center_x, center_y, size, op=math.floor):
        """Read a window centered on specified coordinates.

        Args:
            center_x: X coordinate (longitude/easting) of center point.
            center_y: Y coordinate (latitude/northing) of center point.
            size: Size of window in pixels (square window).
            op: Operation to apply when converting coordinates to pixels. Defaults to math.floor.

        Returns:
            numpy.ndarray: Raster data for the window around the specified coordinates.
        """
        return self.read_windows(self.windows_for_center(center_x, center_y, size, op))

    def read_bound(self, bounds):
        """Read data from a bounding box.

        Args:
            bounds: Tuple of (left, bottom, right, top) coordinates.

        Returns:
            numpy.ndarray: Raster data for the specified bounding box.
        """

        windows = self.src_info.window(*bounds)
        return self.read_windows(windows)


class MultiRasterReader(AbstractRasterReader):
    """Multi-raster file reader for reading multiple aligned rasters.

    Reads multiple raster files as a single combined dataset, with support for
    different resolutions and coordinate systems. Automatically handles
    reprojection and resampling to align all rasters to a reference grid.

    Warning:
        This class should either be thread-safe or properly copied for parallel mapping.

    Todo:
        - Check VRT implementation
        - Improve handling of different projections

    Attributes:
        path: List of paths to geotiff files.
        bands_list: List of band selection configurations for each raster.
        transformer: List of transformation functions for each raster.
        interpolation: List of resampling methods for each raster.
        n_raster: Number of rasters being read.
        reference_index: Index of the reference raster for spatial alignment.
        reader: List of rasterio file readers.
        src_info: List of raster metadata for each file.
        read_profile: Rasterio read configuration.
        n_band: Total number of bands across all rasters.
        sharing: Whether file sharing is enabled.
    """

    def __init__(self, paths: List[str],
                 bands_list: Union[List[Band], None],
                 transformer,
                 interpolation: Union[List[Union[Resampling,  None]], None] = None,
                 reference_index: int = 0,
                 read_profile=None,
                 sharing = False):
        """Initialize multi-raster reader.

        Args:
            paths: List of paths to geotiff files to read.
            bands_list: List of band configurations, one per raster file.
            transformer: List of transformation functions, one per raster.
            interpolation: List of resampling methods for each raster. Defaults to None (nearest neighbor).
            reference_index: Index of raster to use as spatial reference. Defaults to 0.
            read_profile: Rasterio read profile configuration. Defaults to None.
            sharing: Enable file sharing mode. Defaults to False.
        """

        super().__init__(paths[reference_index],
                         bands_list[reference_index],
                         transformer[reference_index],
                         interpolation[reference_index],
                         read_profile,
                         sharing)

        self.n_raster = len(paths)

        if interpolation is None:
            interpolation = [Resampling.nearest for _ in range(self.n_raster)]
        else:
            interpolation = [Resampling.nearest if r is None else r for r in interpolation]

        self.interpolation = interpolation

        self.bands_list = MultiRasterReader.validate_list(bands_list, "in_bands_list", self.n_raster)
        self.transformer = MultiRasterReader.validate_list(transformer, "normalizer", self.n_raster)
        self.interpolation:  Union[List[Union[Resampling,  None]], None]  = interpolation

        self.path = paths

        self.reader = None
        self.reader: list = [None for _ in range(len(paths))]

        self.src_info = []
        for p in paths:
            self.src_info.append(RasterInfo.from_file(p))

        if read_profile is None:
            self.read_profile = get_read_profile()
        else:
            self.read_profile = read_profile

        self.n_band = 0
        self.bands_list = bands_list
        for p, b in zip(paths, self.bands_list):
            if b is None:
                with rasterio.open(p, 'r', **self.read_profile) as reader:
                    self.n_band += reader.count
            else:
                self.n_band += len(b)

            self.reference_index = reference_index

    def __repr__(self):
        return f"MultiRasterReader({self.path}, {self.bands_list}, {self.transformer}, {self.sharing})"

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__init__(self.path,
                        self.bands_list,
                        self.transformer,
                        self.interpolation,
                        self.reference_index,
                        self.read_profile,
                        self.sharing)

        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)

        path = copy.deepcopy(self.path)
        bands_list = copy.deepcopy(self.bands_list)
        transformer = copy.deepcopy(self.transformer)
        interpolation = copy.deepcopy(self.interpolation),
        read_profile = copy.deepcopy(self.read_profile)
        result.__init__(path, bands_list, transformer, interpolation, self.reference_index, read_profile, self.sharing)

        return result

    def __enter__(self):
        self.reader = [rasterio.open(p, 'r', **self.read_profile, sharing= self.sharing) for p in self.path]
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        for r in self.reader:
            r.close()
        self.reader = None

    def ref_raster(self):
        """Get the path of the reference raster.

        Returns:
            str: Path to the reference raster file.
        """
        return self.path[self.reference_index]

    def ref_raster_info(self):
        """Get metadata information of the reference raster.

        Returns:
            RasterInfo: Raster metadata including CRS, transform, dimensions.
        """
        return self.src_info[self.reference_index]

    @staticmethod
    def validate_list(var, var_name, num):
        """Validate list parameter has correct size.

        Args:
            var: Variable to validate (list, None, or single value).
            var_name: Name of variable for error messages.
            num: Expected list size.

        Returns:
            list: Validated list of correct size.

        Raises:
            ValueError: If var is a list of wrong size or invalid type.
        """
        if hasattr(var, '__len__'):
            if len(var) != num:
                raise ValueError(f"{var_name} should be None or a list of size {num},"
                                 f" {len(var)} found instead")
        else:
            if var is None:
                var = [None for _ in range(num)]
            else:
                raise ValueError({"None or list expected for the selected band"})

        return var

    def read_windows_around_coordinate(self, center_x, center_y, size, op= math.floor):
        """Read a window centered on specified coordinates from all rasters.

        Args:
            center_x: X coordinate (longitude/easting) of center point.
            center_y: Y coordinate (latitude/northing) of center point.
            size: Size of window in pixels (square window).
            op: Operation to apply when converting coordinates to pixels. Defaults to math.floor.

        Returns:
            numpy.ndarray: Combined raster data for the window around the specified coordinates.
        """
        return self.read_windows(self.windows_for_center(center_x, center_y, size, math.floor))


    def read_windows(self, window: Window):
        """Read data from a specific window across all rasters.

        Args:
            window: Rasterio window defining the area to read.

        Returns:
            numpy.ndarray: Combined raster data for the specified window.
        """
        bounds = self.ref_raster_info().window_bounds(window)
        return self.read_bound(bounds)


    def _read_windows(self, windows: List[Window]):
        """Internal method to read from multiple windows across all rasters.

        Args:
            windows: List of windows, one per raster file.

        Returns:
            numpy.ndarray: Combined and stacked raster data.
        """
        # TODO manage manage resampling
        #rasterio.windows.from_bounds

        # we read the real window, but change the resolution to "size"
        ref_size = (round(windows[self.reference_index].height), round(windows[self.reference_index].width))

        data = []

        for r, b, norm, interpol, source_window in\
                zip(self.reader, self.bands_list, self.transformer, self.interpolation, windows):
            if b.selected1 is not None:
                d = r.read(b.selected1, window=source_window, boundless=True,
                           out_shape=ref_size, resampling=interpol)
            else:
                d = r.read(window=source_window, boundless=True,
                           out_shape=ref_size, resampling=interpol)

            if norm is not None:
                norm(d)

            data.append(d)

        data = numpy.vstack(data)

        return data

    def read_bound(self, bounds):
        """Read data from a bounding box across all rasters.

        Automatically handles reprojection if rasters have different coordinate
        reference systems.

        Args:
            bounds: Tuple of (left, bottom, right, top) coordinates in reference CRS.

        Returns:
            numpy.ndarray: Combined raster data for the specified bounding box.
        """

        windows = []
        for info in self.src_info:
            if self.ref_raster_info().crs == info.crs:
                other_bounds = bounds
            else:
                other_bounds = rasterio.warp.transform_bounds(self.ref_raster_info().crs, info.crs, *bounds)

            windows.append(info.window(*other_bounds))

        return self._read_windows(windows)



