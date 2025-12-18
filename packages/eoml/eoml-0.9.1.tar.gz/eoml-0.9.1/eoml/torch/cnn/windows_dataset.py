import math
from bisect import bisect_right
from typing import List

import torch
from eoml.raster.raster_reader import AbstractRasterReader
from eoml.torch.cnn.torch_utils import conv_out_size
from rasterio.coords import BoundingBox
from rasterio.windows import Window
from torch.utils.data import Dataset


class WindowsTrainingDataset(Dataset):
    """
    Basic implementation of training dataset, receive a list of images, cut windows through them and store everything
    in memories

    Todo need to be finished
    """
    def __init__(self,
                 input_raster_reader: AbstractRasterReader,
                 target_raster_reader: List[AbstractRasterReader],
                 size,
                 stride,
                 padding,
                 transform_output):

        self.input_raster_reader = input_raster_reader

        self.target_raster_readers = target_raster_reader

        self.size = size
        self.stride = stride
        self.padding = padding

        self.transform_output = transform_output

        self.conv_sum = []

        self.radius = math.floor(size)


    def compute_stats(self):

        sum = 0
        conv_sum = []
        for raster in self.target_raster_readers:
            width = conv_out_size(raster.ref_raster_info().width, self.size, self.stride, self.padding)
            height = conv_out_size(raster.ref_raster_info().height, self.size, self.stride, self.padding)

            sum+= width*height
            self.conv_sum.append(sum)

    def _find_image_index(self, conv_b):
        """index of the image
        bisect right return the index (on the right in case of equality to insert value to keep the list ordered)
        """
        index_image = bisect_right(self.conv_sum, conv_b) - 1
        index_in_image = conv_b - self.conv_sum[index_image]

        con_per_row = conv_out_size(self.target_raster_readers[index_image].ref_raster_info().width, self.size, self.stride, self.padding)

        col, row = divmod(index_in_image, con_per_row)

        return index_image, col, row
    def generate_input(self, index_image, col, row):
        # this way would interpol the input.
        out_reader = self.target_raster_readers[index_image]
        target_window = Window(col - self.radius, row - self.radius, self.size, self.size)

        bounding_box = out_reader.ref_raster_info().window_bounds(target_window)

        out_reader.read_windows_around_coordinate(target_window)

        with self.input_raster_reader:
            input = self.input_raster_reader.read_bound(bounding_box)

        with out_reader:
            output = out_reader.read_windows_around_coordinate(target_window)

        return input, output

    def __len__(self):
        return len(self.conv_sum[-1])

    def __getitem__(self, idx):

        if hasattr(idx, '__iter__'):
            return self._get_items(idx)

        if isinstance(idx, int):
            return self._get_one_item(idx)

        if isinstance(idx, slice):
            # Get the start, stop, and step from the slice
            return self._get_items(range(idx.start, idx.stop, idx.step))

    def _get_items(self, iterable):
        datas = []
        labels = []
        for key in iterable:
            data, label = self._get_one_item(key)
            datas.append(data)
            labels.append(label)
        return [datas, labels]

    def _get_one_item(self, idx):
        index_image, col, row = self._find_image_index(idx)

        inputs, output = self.generate_input(self, index_image, col, row)

        inputs = torch.from_numpy(inputs)
        output = torch.from_numpy(output)

        if self.transform_output is not None:
            output = self.transform_output(inputs)

        return inputs, output


