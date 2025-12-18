import torch
from eoml.torch.cnn.map_dataset import MapResultAggregator, BatchMeta, IterableMapDataset
from rasterio.windows import Window


class ConstMemBatchMeta(BatchMeta):

    def __init__(self, window, is_finished, count, worker):
        super().__init__(window, is_finished, worker)
        self.window = window
        self.is_finished = is_finished
        self.count = count
        self.worker = worker


class Buffer:

    def __init__(self, bands, height, width, device):
        self.buffer = None
        self.device = device
        self.stored_height = 0
        self.stored_width = 0
        self.bands = bands

    def store(self, data):
        channel, height, width = data.shape
        # we need a new buffer to avoid writing in the buffer being used for computation on gpu
        # we cound have prefectch number of buffer to solve this issue
        self.buffer = torch.empty((channel, height, width), device=self.device)
        self.buffer[:, 0:height, 0:width] = data
        self.stored_height = height
        self.stored_width = width

    def __getitem__(self, item):
        self.buffer.__getitem__(item)

    def __setitem__(self, key, value):
        self.buffer.__setitem__(key, value)

    @property
    def shape(self):
        return self.bands, self.stored_height, self.stored_width


class IterableMapDatasetConstMem(IterableMapDataset):
    # Create an aligned raster with cropped border to take the convolution into account.
    # If stride is >1, the widows starting at the top left corner and size stride X stride
    # will be filled with the value returned by the NN.

    def __init__(self, raster_reader, kernel_size, target_windows, off_x, off_y, stride=1, batch_size=1024,
                 device="cpu"):

        super().__init__(raster_reader, kernel_size, target_windows, off_x, off_y, stride, batch_size, device)

        self.max_width, self.max_height = self._max_win_size(target_windows, kernel_size)
        self.buffer = Buffer(raster_reader.n_band, self.max_width, self.max_height, device)

    def _max_win_size(self, windows, size):
        # windows is a tuble ((i,j), windows)
        width = max(windows, key=lambda w: w[1].width)[1].width + size
        height = max(windows, key=lambda w: w[1].height)[1].height + size
        return width, height

    def __iter__(self):
        """
        iteratro over the dataset. return at most batch_size data or the number of data needed to finish the current
        block of data.
        :return: data, (target_windows, is_block_finished, worker_id)
        """
        #flush = 0
        for ji, window in self.target_windows:

            #flush +=1
            (col_off, row_off, w_width, w_height) = window.flatten()
            # compute the source windows
            window_source = Window(col_off + self.off_x - self.half_size, row_off + self.off_y - self.half_size,
                                   w_width + self.size - 1, w_height + self.size - 1)

            np_buff = self.read_windows(window_source)

            self.buffer.store(torch.from_numpy(np_buff))

            for sample, meta in self.extract_tensor_iter(self.buffer, self.batch_size):
                meta.window = window
                yield sample, meta

            #if flush == self.flush_threshold:
            #    flush = 0
            #    del sample
            #    gc.collect()
            #    torch.cuda.empty_cache()

    def extract_tensor_iter(self, data, batch_size):
        channel, height, width = data.shape

        height = height - self.size + 1
        width = width - self.size + 1

        samples = []

        count = 0

        for i in range(0, height):
            for j in range(0, width):
                if count == batch_size:
                    yield torch.stack(samples, dim=0), ConstMemBatchMeta(None, False, count, self.worker_id)
                    samples = []
                    count = 0
                source_w = self.buffer.buffer.narrow(1, i, self.size).narrow(2, j, self.size)
                samples.append(source_w)
                count += 1

        # file the batch with empty sample
        valid_count = count
        while count < batch_size:
            # seems to be a bit faster
            self.buffer.buffer.narrow(1, 0, self.size).narrow(2, 0, self.size)
            #samples.append(torch.empty(channel, self.size, self.size,device=self.device))
            count += 1

        yield torch.stack(samples, dim=0), ConstMemBatchMeta(None, True, valid_count, self.worker_id)


class MapResultAggregatorConstMem(MapResultAggregator):

    def __init__(self, path_out, transform_result_f, n_windows, write_profile):
        super().__init__(path_out, transform_result_f, n_windows, write_profile)

    def submit_result(self, values, meta: ConstMemBatchMeta):
        values = values[:meta.count]
        super().submit_result(values,meta)




