"""PyTorch utility functions for neural network operations.

This module provides helper functions for PyTorch-based deep learning, including
convolution size calculations, custom collation functions for data loaders, pixel
extraction utilities, and grid alignment functions for geospatial raster data.
"""

import logging
import math

import numpy as np
import torch
from rasterio.transform import xy, rowcol, guard_transform
from rasterio.warp import Affine
from rasterio.windows import Window, transform
from torch.utils.data import default_collate

logger = logging.getLogger(__name__)

def int_to_list(var, size):
    """Convert integer to list or validate list size.

    Used for managing convolution size inputs. Repeats an integer value into a
    list of specified size, or validates that an existing list has the correct size.

    Args:
        var: Integer value to repeat or list to validate.
        size: Target list size.

    Returns:
        list: List of specified size containing the value(s).

    Raises:
        Exception: If var is a list of wrong size.
    """
    if isinstance(var, int):
        list_var = [var for i in range(size)]
    else:
        if len(var) != size:
            raise Exception(" Input should have size n")
        list_var = var

    return list_var


def conv_out_size(in_size, conv, stride, padding):
    """Calculate output size of a convolution along one dimension.

    Args:
        in_size: Input size in pixels.
        conv: Convolution kernel size.
        stride: Convolution stride.
        padding: Padding size.

    Returns:
        int: Output size after convolution.
    """
    return math.floor((in_size - conv + 2 * padding) / stride + 1)


def conv_out_sizes(in_size, convs, strides, paddings):
    """Calculate output sizes of a series of convolutions.

    Args:
        in_size: Initial input size in pixels.
        convs: List of convolution kernel sizes (or single value).
        strides: List of strides (or single value).
        paddings: List of padding sizes (or single value).

    Returns:
        list: List of output sizes after each convolution, including initial size.
    """
    n_layer = len(convs) if hasattr(convs, '__len__') else 1
    n_layer = len(strides) if hasattr(strides, '__len__') else n_layer
    n_layer = len(paddings) if hasattr(paddings, '__len__') else n_layer

    convs = int_to_list(convs, n_layer)
    strides = int_to_list(strides, n_layer)
    paddings = int_to_list(paddings, n_layer)

    sizes = [in_size]
    for conv, stride, padding in zip(convs, strides, paddings):
        sizes.append(conv_out_size(sizes[-1], conv, stride, padding))
    return sizes

class PixelAt:
    """Extract specific pixel values from an array.

    Can use lists to get multiple values at once.

    Attributes:
        c: Channel index(es).
        h: Height/row index(es).
        w: Width/column index(es).
    """

    def __init__(self, c, h, w):
        self.c = c
        self.h = h
        self.w = w

    def __call__(self, array):
        return pixel_at(array, self.c, self.h, self.w)

class PixelAtBand:
    def __init__(self, h, w):
        self.h = h
        self.w = w

    def __call__(self, array):
        return pixel_at_band(array, self.h, self.w)


class PixelAtBandSkipValue:

    def __init__(self, h, w, skip):
        """

        :param h:
        :param w:
        :param skip: if the value is in any of the return array, we skip it
        """
        self.h = h
        self.w = w
        self.skip = skip

    def __call__(self, array):
        out = pixel_at_band(array, self.h, self.w)

        if (out == self.skip).any():
            return None

        return out

def center_pixel(array):
    """
    look for the central pixel of an array and return it. Pixel at is error-prone but more efficient
    :param array:
    :return the centrer pixels values (all the band):
    """
    h, w = array.shape

    if h % 2 != 1 or w % 2 != 1:
        raise "h,w has no clear center, size should be odd"

    center_h = math.ceil(h / 2)
    center_w = math.ceil(w / 2)

    return array[:, center_h, center_w]


def pixel_at(array, c, h, w):
    """
    Return the pixel at a given position and return an array (scalar value are transformed to a vector of size 1
    :param array: to extract value from
    :param c: chanel to extract value from (use a list to extract multiple value
    :param h: height index (use a list to extract multiple value
    :param w: width index (use a list to extract multiple value
    :return:
    """
    # can use a list to get multiple value
    v = array[c, h, w]
    if not isinstance(v, np.ndarray):
        v = np.array([v])
    return v

def pixel_at_band(array, h, w):
    """
    Return the pixel at a given position and return an array (scalar value are transformed to a vector of size 1
    :param array: to extract value from
    :param c: chanel to extract value from (use a list to extract multiple value
    :param h: height index (use a list to extract multiple value
    :param w: width index (use a list to extract multiple value
    :return:
    """
    # can use a list to get multiple value
    v = array[:, h, w]
    if not isinstance(v, np.ndarray):
        v = np.array([v])
    return v



def multi_input_training_collate(batch):
    """
    custom collate function, used then there is multiple input.
    :param batch:
    :return: collated data separated by batch
    """

    data_entries = [[] for _ in range(len(batch[0]))]

    for b in batch:
        for i, entry in enumerate(b):
            data_entries[i].append(entry)
    # need index 0 as collate keep the outside list
    out = list(map(lambda x: default_collate(x), data_entries))


    # return the input out output separated
    return out[:-1], out[-1]

def batch_collate(batch):
    """
    custom collate function, used when we use a batch sampler.
    :param batch:
    :return: collated data and metadata separated
    """
    return batch[0]

def meta_data_collate(batch):
    """
    custom collate function, used when the __get_item__/the iterator return data, metadata. Applly default collate to
    the data and left the meta-data untransformed.
    Apply the default collate the
    :param batch:
    :return: collated data and metadata separated
    """
    data = []
    meta = []
    for b in batch:
        data.append(b[0])
        meta.append(b[1])

    return torch.utils.data.default_collate(data), meta

def multi_input_meta_data_collate(batch):
    """
    custom collate function, used when the __get_item__/the iterator return multiple data, and 1 metadata. Applly default collate to
    each data independantly and left the meta-data untransformed.
    Apply the default collate the
    :param batch:
    :return: collated data and metadata separated
    """
    data_entries = [[] for _ in range(len(batch[0][0]))]
    sample, meta = batch[0]
    #skip le last as it is meta data

    for i, entry in enumerate(sample):
        data_entries[i].append(entry)

    # we get an outside list so we take index 0
    out = list(map(lambda x: default_collate(x)[0], data_entries))

    return out, [meta]



def no_collate(batch):
    """
        Do not transform data to tensor. flatten numpy array and separate data from meta data
    """
    data = []
    meta = []

    for b in batch:
        d = b[0].numpy().reshape(len(b[0]), len(b[0][0]))
        np.nan_to_num(d, copy=False, )
        data.append(b[0].numpy().reshape(len(b[0]), len(b[0][0])))
        meta.append(b[1])

    return data, meta


def align_grid_deprecated(source_meta, bounds, size):
    """
    Given the bounds we want to apply convolution to, the function will align the bound to the best matching pixel.
    The bounds are computed for the center pixel of the windows to always be inside. TODO add offset?
    :param source_meta:
    :param bounds:
    :param size:
    :return:
    """
    ##align the grids taking into account the covolution on the border

    ## take into account shifted coordinate system

    half_size = size // 2

    transform = source_meta["transform"]

    # inverted coordinate
    assert transform.e < 0

    # grid bound in the source grid coordinate

    (bottom, left) = rowcol(transform, bounds.left, bounds.bottom, op)
    (top, right) = rowcol(transform, bounds.right, bounds.top, op)


    # compute the target bounds taking into account the convolution
    left = max(0, left - half_size) + half_size
    bottom = min(bottom + half_size, source_meta["height"]) - half_size

    top = max(0, top - half_size) + half_size
    right = min(right + half_size, source_meta["width"]) - half_size

    # dimension of the bound grid
    width = right - left
    height = bottom - top

    (west, north) = xy(transform, top, left, offset="ul")

    # based on transformation from bound. specify the left, top pixel and pixel size same as original)
    target_transform = Affine.translation(west, north) * Affine.scale(transform.a, transform.e)

    # lef top is the offset
    return target_transform, width, height, left, top


def align_grid(src_transform, bounds, r_width, r_height, size, shrink_for_conv=False, precision=0.01):
    """
    Given the bounds we want to apply convolution to, the function will align the bound to the best matching pixel.
    The bounds are computed for the center pixel of the windows to always be inside. TODO add offset?
    :param transform:
    :param bounds:
    :param size:
    :return:
    """
    ##align the grids taking into account the covolution on the border

    ## take into account shifted coordinate system

    half_size = size // 2

    # grid bound in the source grid coordinate

    window = aligned_bound(bounds.left, bounds.bottom, bounds.right, bounds.top, src_transform, precision=precision)

    left = window.col_off
    right = left + window.width

    top = window.row_off
    bottom = top + window.height

    # compute the target bounds taking into account the convolution
    if shrink_for_conv:
        left = max(0, left - half_size) + half_size
        bottom = min(bottom + half_size, r_height) - half_size + 1

        top = max(0, top - half_size) + half_size
        right = min(right + half_size, r_width) - half_size + 1

        # dimension of the bound grid
        # new windows with convolution inside
        window = Window(left, top, right - left, bottom - top)

    # from window_transform(windows)

    width = right - left
    height = bottom - top

    gtransform = guard_transform(src_transform)
    target_transform = transform(window, gtransform)

    #(west, north) = xy(transform, top, left, offset="ul")

    # based on transformation from bound. specify the left, top pixel and pixel size same as original)
    #target_transform = Affine.translation(west, north) * Affine.scale(transform.a, transform.e)

    # lef top is the offset
    return target_transform, width, height, left, top

def aligned_bound(left, bottom, right, top, transform, precision=0.01):
    """
    Compute the input windows with a shrink of 1 pixel.
    We assume pixel is area. pixel "point" is located at the top left of the pixel and bounding is the real bounding
    box. This mean boding box is effectively at pixel (0, 0) and (length, length). the actual array pixel as last
    pixel at length-1, length-1

    the pixel is included if precision percent of it is covered by the raw raster
    """

    def idx(x):
        return x

    #index invert coordinate order ie rowcol (could use row col
    bottom, left = rowcol(transform, left, bottom, op=idx)  #transform.index(left, bottom, op=idx)
    top, right = rowcol(transform, right, top, op=idx)     # transform.index(right, top, op=idx)

    # top left pixel if contained more than precision from the top lef corner of the pixel we need to round up
    left = _round_high(left, precision) # the index match the bound
    top = _round_high(top, precision)

    # we need to be very close to the bottom right of the pixel (it mean it includ almost all the pixel, if not round down
    bottom = _round_low(bottom, precision)-1 #the bound is at index + 1
    right = _round_low(right, precision)-1

    return Window(left, top, right-left, bottom-top)


def _round_low(value, precision):

    if math.ceil(value)-value < precision:
        value = math.ceil(value)
    return math.floor(value)


def _round_high(value, precision):
    # if pixel of input almost covered we use it anyway (the the left and top pixel. covered mean close to floor)
    if value - math.floor(value) < precision:
        value = math.floor(value)

    return math.ceil(value)
