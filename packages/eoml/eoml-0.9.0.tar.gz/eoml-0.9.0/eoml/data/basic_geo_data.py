"""Basic geographical data structures for storing raster samples with metadata.

This module defines core data structures for representing geospatial training samples,
including headers with geometry information and complete samples combining raster data
with labels and metadata.
"""

import math

import numpy as np
import rasterio

from eoml import get_read_profile, get_write_profile


class GeoDataHeader:
    """Header containing metadata for a geospatial data sample.

    Stores identifying information about a geographic sample including its unique identifier,
    spatial geometry (typically a point), and source file name.

    Attributes:
        idx: Unique identifier for the sample (from vector file or assigned)
        geometry: Shapely geometry object representing the sample location
        file_name: Name of the source file containing this sample
    """

    def __init__(self, idx, geometry, file_name):
        """Initialize a GeoDataHeader.

        Args:
            idx: Unique identifier for the sample
            geometry: Shapely geometry object (typically Point) for sample location
            file_name: Source filename where this sample originates
        """
        self.idx = idx
        self.geometry = geometry
        self.file_name = file_name

    def __eq__(self, other):
        """Check equality based on idx, geometry, and file_name.

        Args:
            other: Another object to compare against

        Returns:
            True if all attributes match, False otherwise
        """
        if isinstance(other, GeoDataHeader):
            return self.idx == other.idx and self.geometry == other.geometry and self.file_name == other.file_name
        return NotImplemented

    def __repr__(self):
        """Return string representation of the header.

        Returns:
            String showing id, geometry WKT, and filename
        """
        return f"GeoDataHeader(id:{self.idx}, geometry:{self.geometry.wkt}, file_name:{self.file_name})"


class BasicGeoData:
    """Complete geospatial sample with header, raster data, and target label.

    Represents a training sample combining metadata (header), multi-band raster data
    (typically a small image window), and a target value (class label or regression value).

    Attributes:
        header: GeoDataHeader containing sample metadata
        data: NumPy array of raster data, typically shape (bands, height, width)
        target: Target value (int for classification, float for regression, or array)
    """

    def __init__(self, header, data, target):
        """Initialize a BasicGeoData sample.

        Args:
            header: GeoDataHeader with sample metadata
            data: NumPy array containing raster data
            target: Target value(s) for supervised learning
        """
        self.header = header
        self.data = data
        self.target = target

    @property
    def header(self):
        """Get the sample header.

        Returns:
            GeoDataHeader instance
        """
        return self._header

    @header.setter
    def header(self, value):
        """Set the sample header.

        Args:
            value: GeoDataHeader instance
        """
        self._header = value

    @property
    def data(self):
        """Get the raster data array.

        Returns:
            NumPy array of raster data
        """
        return self._data

    @data.setter
    def data(self, value):
        """Set the raster data array.

        Args:
            value: NumPy array containing raster data
        """
        self._data = value

    @property
    def target(self):
        """Get the target label or value.

        Returns:
            Target value (scalar or array)
        """
        return self._target

    @target.setter
    def target(self, value):
        """Set the target label or value.

        Args:
            value: Target value for the sample
        """
        self._target = value

    def __eq__(self, other):
        """Check equality based on header, data, and target.

        Args:
            other: Another object to compare against

        Returns:
            True if all components match (including NaN values), False otherwise
        """
        if isinstance(other, BasicGeoData):
            return self.header == other.header and np.array_equal(self.data, other.data, equal_nan=True)\
                   and self.target == other.target

        return NotImplemented

    def to_file(self, path, ref):
        """Write the raster data to a GeoTIFF file with proper georeferencing.

        Exports the sample's raster data to a georeferenced GeoTIFF using the coordinate
        reference system and transform from a reference raster. The output raster is
        centered on the sample's geometry point.

        Args:
            path: Output path for the GeoTIFF file
            ref: Path to reference raster file for CRS and transform information

        Returns:
            None. Writes GeoTIFF to specified path

        Raises:
            IOError: If reference file cannot be opened or output cannot be written
        """
        with rasterio.open(ref) as src:
            #aff = src.transform
            #pixelSizeX = aff[0]
            #pixelSizeY = -aff[4]

            crs = src.crs
            x = self.header.geometry.x
            y = self.header.geometry.y

            row, col = src.index(x, y, op=math.floor)

            sizeX = self.data.shape[1] / 2
            sizeY = self.data.shape[1] / 2

            west, north = src.xy(row-sizeX, col-sizeY)
            east, south = src.xy(row + sizeX, col + sizeY)
            #west, south, east, north = self.header.geometry.extends


            transform = rasterio.transform.from_bounds(west, south, east, north,
                                                   self.data.shape[1], self.data.shape[2])


        profile = get_write_profile()

        profile.update({"height": self.data.shape[1],
                        "width": self.data.shape[2],
                        "count": self.data.shape[0],
                        "dtype": self.data.dtype,
                        "crs": crs,
                        "transform": transform})

        with rasterio.open(path, "w", **profile) as src:
            src.write(self.data)


    def __repr__(self):
        """Return string representation of the sample.

        Returns:
            String showing header, data shape/dtype, and target
        """
        return f"BasicGeoData(header:{self.header.__repr__()}, data:{self.data.__repr__()}, target:{self.target.__repr__()})"