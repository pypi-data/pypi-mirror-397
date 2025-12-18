"""Output transformation classes for neural network predictions.

This module provides classes for transforming raw neural network outputs into
usable formats for geospatial mapping, including classification, regression,
and probability outputs.
"""

from typing import List

import numpy as np


class OutputTransformer:
    """Abstract base class for transforming neural network outputs.

    Defines interface for converting raw NN outputs to map-ready values.

    Attributes:
        _shape: Shape of the output data.
        _dtype: Data type for output values.
        _nodata: No-data value for invalid outputs.
    """
    def __init__(self, shape, dtype, nodata):
        self._shape = shape
        self._dtype = dtype
        self._nodata = nodata

    def __call__(self, v):
        ...
    @property
    def shape(self):
        """
        shape of the output
        :return:
        """
        return self._shape

    @property
    def bands(self):
        """
        shape of the output
        :return:
        """
        return self.shape[0]
    @property
    def dtype(self):
        """
        shape of the input
        :return:
        """
        return self._dtype

    @property
    def nodata(self):
        """
        shape of the input
        :return:
        """
        return self._nodata


class ArgMax(OutputTransformer):
    """Return the index of the highest neural network output.

    Performs argmax operation for classification tasks.

    Attributes:
        dtype: Data type for output indices. Defaults to "int16".
        nodata: Value for invalid outputs. Defaults to -1.
    """
    def __init__(self, dtype="int16", nodata=-1):
        super().__init__([1], dtype, nodata)

    def __call__(self, vec):
        return np.argmax(vec, axis=1).astype(self.dtype)


class ArgMaxToCategory(ArgMax):
    """Transform neural network categories to map category values.

    Performs argmax to find the highest output, then maps the index to a
    specific category value from the provided mapping.

    Attributes:
        category_map: List mapping NN output indices to category values.
        dtype: Data type for output values. Defaults to "int16".
        nodata: Value for invalid outputs. Defaults to -1.
    """
    def __init__(self, category_map: List, dtype="int16", nodata=-1):
        super().__init__(dtype, nodata)
        self.category_map = category_map

    def __call__(self, vec):
        return np.array([self.category_map[x] for x in super().__call__(vec)], dtype=self.dtype)


class Identity(OutputTransformer):
    """Return neural network output as-is with type casting.

    Passes through NN output but casts to specified map format. Output shape
    must be specified in constructor.

    Attributes:
        shape: Shape of the output data.
        dtype: Data type for output values.
        nodata: Value for invalid outputs.
    """
    def __init__(self, shape, dtype, nodata):
        super().__init__(shape, dtype, nodata)

    def __call__(self, vec):
        return vec.astype(self.dtype)


class ToPercentage(OutputTransformer):
    """Convert neural network output to percentage values.

    Multiplies output by 100 and casts to specified type, useful for
    probability or confidence outputs.

    Attributes:
        shape: Shape of the output data. Defaults to [1].
        dtype: Data type for output values. Defaults to "int16".
        nodata: Value for invalid outputs. Defaults to -255.
    """
    def __init__(self, shape=[1], dtype="int16", nodata=-255):
        super().__init__(shape, dtype, nodata)

    def __call__(self, vec):
        return (100*vec).astype(self.dtype)
