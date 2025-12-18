"""
Band management module for raster operations.

This module provides the Band class for managing raster band selections,
supporting both 0-indexed and 1-indexed band numbering systems used by
different rasterio operations.
"""
from pathlib import Path

import rasterio


class Band:
    """
    Manage band numbers with support for both 0-indexed and 1-indexed access.

    This class facilitates working with raster bands by maintaining both
    0-indexed (Python-style) and 1-indexed (rasterio-style) band lists.
    This is particularly useful when interfacing with rasterio, which uses
    1-based indexing for band operations.

    Attributes:
        length (int): Number of bands in the selection.

    Properties:
        selected (list): 0-indexed list of band numbers (Python-style).
        selected1 (list): 1-indexed list of band numbers (rasterio-style).

    Examples:
        >>> # Create a band selection for bands 0, 1, 2
        >>> bands = Band([0, 1, 2])
        >>> print(bands.selected)   # [0, 1, 2]
        >>> print(bands.selected1)  # [1, 2, 3]
        >>>
        >>> # Create from a file
        >>> bands = Band.from_file("path/to/raster.tif")
    """

    def __init__(self, selected):
        """
        Initialize a Band instance with a list of band numbers.

        Args:
            selected (list): List of 0-indexed band numbers to select.

        Raises:
            Exception: If selected is None.

        Examples:
            >>> bands = Band([0, 2, 4])  # Select bands 0, 2, and 4
        """
        if selected == None:
            raise Exception("specify a band range")

        self._selected = selected.copy()
        self._selected1 = [b+1 for b in selected]
        self.length = len(self.selected)

    @classmethod
    def from_file(cls, raster_path:Path):
        """
        Create a Band instance from a raster file, selecting all bands.

        This class method reads a raster file and creates a Band object
        containing all bands present in the file.

        Args:
            raster_path (str): Path to the raster file.

        Returns:
            Band: Band instance containing all bands from the raster.

        Examples:
            >>> bands = Band.from_file("/path/to/satellite_image.tif")
            >>> print(len(bands))  # Number of bands in the file
        """
        with rasterio.open(raster_path) as src:
            length = src.count

        selected = list(range(length))

        return cls(selected)

    def remove(self, band):
        """
        Remove a band from the selection.

        Args:
            band (int): 0-indexed band number to remove.

        Examples:
            >>> bands = Band([0, 1, 2, 3])
            >>> bands.remove(2)  # Remove band 2
            >>> print(bands.selected)  # [0, 1, 3]
        """
        self._selected.remove(band)
        self._selected1.remove(band+1)

    def append(self, band):
        """
        Add a band to the selection.

        Args:
            band (int): 0-indexed band number to add.

        Examples:
            >>> bands = Band([0, 1])
            >>> bands.append(2)  # Add band 2
            >>> print(bands.selected)  # [0, 1, 2]
        """
        self._selected.append(band)
        self._selected1.append(band+1)

    @property
    def selected(self):
        """
        Get the 0-indexed band list (Python-style).

        Returns:
            list: List of 0-indexed band numbers.
        """
        return self._selected

    @property
    def selected1(self):
        """
        Get the 1-indexed band list (rasterio-style).

        Returns:
            list: List of 1-indexed band numbers.
        """
        return self._selected1

    def __len__(self):
        """
        Get the number of bands in the selection.

        Returns:
            int: Number of selected bands.
        """
        return self.length
