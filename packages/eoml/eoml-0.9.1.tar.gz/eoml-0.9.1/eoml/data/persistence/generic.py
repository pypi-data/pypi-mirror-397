"""Generic data persistence interfaces for geospatial machine learning datasets.

This module defines abstract base classes and interfaces for storing and retrieving
geospatial training data. It provides a data access object (DAO) pattern for managing
labeled geospatial samples with associated metadata, supporting various backend
storage implementations (e.g., LMDB, HDF5, etc.).

The module includes serialization interfaces for both data and headers, enabling
flexible storage formats while maintaining a consistent access API.
"""

from abc import ABC, abstractmethod

from eoml.data.basic_geo_data import BasicGeoData, GeoDataHeader


class BasicGeoDataDAO(ABC):
    """Abstract data access object for geospatial sample databases.

    Defines the minimum interface required for reading from and writing to
    a geospatial sample database. Implementations should provide efficient
    storage and retrieval of raster data with associated labels and metadata.
    """

    @abstractmethod
    def n_sample(self):
        """Number of sample in the db"""
        pass

    @abstractmethod
    def get(self, num: int) -> BasicGeoData:
        """
        Get the sample num
        :param num: index of the sample to get
        :return: Full sample with header
        """
        pass

    def get_header(self, key: int) -> GeoDataHeader:
        """
        Get the header for sample num
        :param num: index of the sample to get
        :return: header of the sample
        """
        pass

    @abstractmethod
    def get_data(self, num: int):
        """
        Only get the input and expected output of the nn
        :param num: index of the sample to get
        :return: Full sample with header
        """
        pass

    @abstractmethod
    def get_output(self, num: int):
        """
        get the output for num
        :param num:
        :return:
        """
        pass

    @abstractmethod
    def get_header_key(self, header: GeoDataHeader):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    # @abstractmethod
    # def remove(self, value):
    #    pass

    @abstractmethod
    def save(self, geodata: BasicGeoData):
        """
        Insert sample in the db
        :param geodata: data to save in the db
        :return: nothing
        """
        pass

    @abstractmethod
    def __len__(self):
        pass


class GeoDataReader:
    """Reader class for accessing geospatial dataset databases.

    Provides high-level read operations on geospatial sample databases,
    wrapping a DAO implementation with convenient access methods.

    Attributes:
        dao: Data access object providing low-level database operations.
    """

    def __init__(self, dao: BasicGeoDataDAO):
        self.dao: BasicGeoDataDAO = dao

    def n_sample(self):
        return self.dao.n_sample()

    def get(self, key: int) -> BasicGeoData:
        return self.dao.get(key)

    def get_header(self, key: int) -> GeoDataHeader:
        return self.dao.get_header(key)

    def get_output(self, num: int):
        """
        get the output for num
        :param num:
        :return:
        """
        return self.dao.get_output(num)

    def get_data(self, key: int):
        return self.dao.get_data(key)

    def get_header_key(self, header: GeoDataHeader):
        return self.dao.get_header_key(header)

    def def_get_output_dic(self):
        """return a dictionary with id:output as entries"""
        return {i: self.dao.get_output(i) for i in range(len(self.dao))}

    def get_sample_id_output_dic(self):
        """return a dictionary with id IN THE GEOPACKAGE and the output"""
        return {self.dao.get_header(i).idx: self.dao.get_output(i) for i in range(len(self.dao))}

    def get_sample_id_db_key_dic(self):
        """return a dictionary with id:output as entries"""
        return {self.dao.get_header(i).idx: i for i in range(len(self.dao))}

    def _check_db_match(self, db_reader2):
        with self, db_reader2:

            if self.n_sample() !=db_reader2.n_sample():
                return False

            id_key1 = self.get_sample_id_db_key_dic()
            id_key2 = db_reader2.get_sample_id_db_key_dic()

            for idx, k1 in id_key1.items():
                k2 = id_key2.get(idx, None)
                if k2 is None:
                    return False
                s1 = self.get(k1)
                s2 = db_reader2.get(k2)

                if s1 != s2:
                    return False
            return True


    def open(self):
        self.dao.open()

    def close(self):
        self.dao.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


class GeoDataWriter:
    """Writer class for saving geospatial samples to databases.

    Provides high-level write operations for storing geospatial samples,
    wrapping a DAO implementation.

    Attributes:
        dao: Data access object providing low-level database operations.
    """
    def __init__(self, dao: BasicGeoDataDAO):
        self.dao = dao

    def save(self, geodata):
        self.dao.save(geodata)

    def open(self):
        self.dao.open()

    def close(self):
        self.dao.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

class GeoDataHeaderSerializer(ABC):
    """Abstract serializer for geospatial data headers.

    Defines interface for converting GeoDataHeader objects to and from
    byte representations for storage.
    """
    @abstractmethod
    def serialize(self, header: GeoDataHeader):
        """
        serialize the header to bytes
        :return: bytes representation of the headers
        """
        pass

    @abstractmethod
    def deserialize(self, msg):
        """
        Deserialize the header
        :param msg: data to deserialize
        :return: a GeoDataHeader
        """
        pass


class GeoDataSerializer(ABC):
    """Abstract serializer for geospatial dataset arrays.

    Defines interface for converting data arrays (typically numpy arrays)
    to and from byte representations for storage.
    """

    @abstractmethod
    def serialize(self, data: BasicGeoData):
        """

        :param data: dataset to be serialized
        :return: bytes representation of the data
        """
        pass

    @abstractmethod
    def deserialize(self, msg):
        """

        :param msg: serialised representation
        :return: the geodataset
        """
        pass
