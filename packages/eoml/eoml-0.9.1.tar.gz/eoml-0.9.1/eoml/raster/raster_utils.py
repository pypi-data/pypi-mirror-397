import json

import numpy as np
import rasterio
from rasterio.transform import TransformMethodsMixin
from rasterio.windows import WindowMethodsMixin


class RasterInfo(WindowMethodsMixin, TransformMethodsMixin):

    def __init__(self, transform, height, width, crs, bounds):
        self.transform = transform
        self.height = height
        self.width = width
        self.crs = crs
        self.bounds = bounds

    @classmethod
    def from_file(cls, path):
        with rasterio.open(path) as src:
            return cls(src.transform, src.height, src.width, src.crs, src.bounds)

def read_gdal_stats(path):
    with open(path) as file:
        # returns JSON object as VN

        # a dictionary
        data = json.load(file)

        bands = data["bands"]
        stats = np.zeros((len(bands),2))


        for b in data["bands"]:
            stats[b["band"]-1]= np.array([b["mean"], b["stdDev"]])
        return stats


def normalize_sigma(data, means, std_devs, n, truncate=False, transform_no_data=None):
    """
    Normalize in place, the values between mean +- n*sigma are compressed between 0 and 1
    :param data: to normalize in place
    :param means: of the original data
    :param std_devs: of the original data
    :param n: number of sigma to map betweren 0 and 1
    :param truncate: weather to truncat value smaller or bigger than 0 or 1 to 0 or 1
    :return: The array changed in place
    """
    for b in range(len(data)):
        data[b] = (1 + (data[b] - means[b]) / (n * std_devs[b])) / 2

    if transform_no_data is not None:
        np.nan_to_num(data, copy=False, nan=transform_no_data, posinf=None, neginf=None)

    if truncate:
        bigger = data > 1
        data[bigger] = 1
        smaller = data < 0
        data[smaller] = 0



class NaNToNumber:
    def __init__(self, number):
        """
        """
        self.number = number
    def __call__(self, data):
        np.nan_to_num(data, copy=False, nan=self.number, posinf=None, neginf=None)
        return data

class SigmaNormalizer:
    def __init__(self, means, std_devs, n, truncate=False, transform_no_data=None):
        """
        Normalize in place, the values between mean +- n*sigma are compressed between 0 and 1
        Object version of function. Usefull for multi threading usinf the spawn methode
        :param means: of the original data
        :param std_devs: of the original data
        :param n: number of sigma to map betweren 0 and 1
        :param truncate: weather to truncat value smaller or bigger than 0 or 1 to 0 or 1
        :return: The array changed in place
        """
        self.means = means
        self.std_devs = std_devs
        self.n = n
        self.truncate = truncate
        self.transform_no_data = transform_no_data


    def __call__(self, data):
        normalize_sigma(data, self.means, self.std_devs, self.n, self.truncate, self.transform_no_data)


class CastSigmaNormalizer:
    def __init__(self, means, std_devs, n, truncate=False, transform_no_data=None, dtype=None):
        """
        Normalize in place, the values between mean +- n*sigma are compressed between 0 and 1
        Object version of function. Usefull for multi threading usinf the spawn methode
        :param means: of the original data
        :param std_devs: of the original data
        :param n: number of sigma to map betweren 0 and 1
        :param truncate: weather to truncat value smaller or bigger than 0 or 1 to 0 or 1
        :return: The array changed in place
        """
        self.means = means
        self.std_devs = std_devs
        self.n = n
        self.truncate = truncate
        self.transform_no_data = transform_no_data
        self.dtype = dtype


    def __call__(self, data):
        if self.dtype is not None:
            data.astype(self.dtype, copy=False)
        normalize_sigma(data, self.means, self.std_devs, self.n, self.truncate, self.transform_no_data)