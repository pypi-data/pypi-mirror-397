"""LMDB-based persistence for geospatial machine learning datasets.

This module provides LMDB (Lightning Memory-Mapped Database) implementations
for storing and retrieving geospatial training data. LMDB offers fast random
access and efficient storage for large datasets, making it ideal for machine
learning workflows.

The implementation uses multiple named databases within a single LMDB environment
to organize different types of data (metadata, headers, inputs, outputs, and indices).

Reference:
    https://stackoverflow.com/questions/32489778/how-do-i-count-and-enumerate-the-keys-in-an-lmdb-with-python
"""

from typing import Literal

import lmdb
from eoml.data.basic_geo_data import GeoDataHeader, BasicGeoData
from eoml.data.persistence.generic import BasicGeoDataDAO, GeoDataReader, GeoDataWriter
from eoml.data.persistence.serializer import MsgpackGeoDataHeaderSerializer, MsgpackGeoDataSerializer

    # Stores geospatial training data in LMDB format with the following structure:
    #     - index_db: Maps (filename, feature_id) to sample keys
    #     - meta_db: Stores metadata (total samples, samples per category, etc.)
    #     - header_db: MessagePack-serialized headers (geometry, source file, source ID)
    #     - data_db: Raster data matrices
    #     - out_db: Target outputs/categories

class LMDBasicGeoDataDAO(BasicGeoDataDAO):
    """LMDB-based data access object for geospatial samples.

    Stores geospatial training data in LMDB format with the following structure:
        - index_db: Maps (filename, feature_id) to sample keys
        - meta_db: Stores metadata (total samples, samples per category, etc.)
        - header_db: MessagePack-serialized headers (geometry, source file, source ID)
        - data_db: Raster data matrices
        - out_db: Target outputs/categories

    Attributes:
        db_path: Path to LMDB database directory.
        map_size_limit: Maximum size of LMDB map in bytes.
        header_serializer: Serializer for GeoDataHeader objects.
        data_serializer: Serializer for numpy array data.
        index_db: Database for sample index mapping.
        meta_db: Database for metadata storage.
        header_db: Database for sample headers.
        data_db: Database for input data.
        category_db: Database for output labels.
        num_sample: Current number of samples in database.
    """
    def __init__(self, db_path, map_size_limit=int(1e+11), header_serializer=None, data_serializer=None):

        super().__init__()

        if header_serializer is None:
            header_serializer = MsgpackGeoDataHeaderSerializer()

        if data_serializer is None:
            data_serializer = MsgpackGeoDataSerializer()

        self.db_path = db_path
        self._lmdb_env = None
        self.category_db = None
        self.data_db = None
        self.header_db = None
        self.meta_db = None
        self.index_db = None

        self.map_size_limit = map_size_limit
        self.header_serializer = header_serializer
        self.data_serializer = data_serializer

        self.index_db_name = self.str_encode("index_db")
        self.meta_db_name = self.str_encode("meta_db")
        self.header_db_name = self.str_encode("header_db")
        self.input_db_name = self.str_encode("data_db")
        self.output_db_name = self.str_encode("out_db")
        self.num_db = 5
        self.num_sample = 0
        self.num_sample_key = self.str_encode("num_sample")

    def str_encode(self, text, encoding="utf-8", errors="strict"):
        """Encode string for db"""
        return text.encode(encoding=encoding, errors=errors)

    def str_decode(self, obj, encoding="utf-8", errors="strict"):
        """decode string"""
        return obj.decode(encoding=encoding, errors=errors)

    def int_encode(self, vale: int,  byteorder: Literal["little", "big"] = 'big'):
        return vale.to_bytes(4, byteorder)

    def int_decode(self, val, byteorder: Literal["little", "big"] = 'big'):
        return int.from_bytes(val, byteorder)

    def n_sample(self):
        return self.fetch_num_sample()

    def sample_number_to_key(self, num):
        """transform the sample id number to a db key (i.e. byte), if bytes received assume it is already encoded
        and do nothing
        """
        # if already bytes. we assume the key is already encoded
        if isinstance(num, bytes):
            return num
        return self.int_encode(num)
        #encode with trailing 0
        #return self.str_encode(f"{num:010}")
        # encode as string
        #return self.str_encode(str(num))

    def header_to_index_key(self, geo_header: GeoDataHeader):
        return self.str_encode(f"{geo_header.idx}-{geo_header.file_name}")

    def get(self, num: int):
        """
        Get the sample numer "num"
        :param num:
        :return:self.str_encode(
        """
        key = self.sample_number_to_key(num)
        data, target = self.get_data(key)

        with self._lmdb_env.begin(write=False, db=self.header_db) as txn:
            header = txn.get(key)
            header = self.header_serializer.deserialize(header)

        return BasicGeoData(header, data, target)

    def get_header(self, num: int) -> GeoDataHeader:
        """
        get the header for num
        :param num:
        :return:
        """
        key = self.sample_number_to_key(num)
        with self._lmdb_env.begin(write=False, db=self.header_db) as txn:
            header = txn.get(key)
            header = self.header_serializer.deserialize(header)

        return header

    def get_output(self, num: int):
        """
        get the output for num
        :param num:
        :return:
        """
        key = self.sample_number_to_key(num)
        with self._lmdb_env.begin(write=False, db=self.category_db) as txn:
            target = txn.get(key)
            target = self.data_serializer.deserialize(target)

        return target

    def get_data(self, num):
        """Only get the data (input and output) for the sample num"""
        key = self.sample_number_to_key(num)

        # Get the input
        with self._lmdb_env.begin(write=False, db=self.data_db) as txn:
            data = txn.get(key)
            data = self.data_serializer.deserialize(data)
        # The output
        target = self.get_output(num)

        return data, target

    def get_header_key(self, header: GeoDataHeader):
        """Only get the data (input and output) for the sample num"""
        key = self.header_to_index_key(header)

        with self._lmdb_env.begin(write=False, db=self.index_db) as txn:
            data = txn.get(key)

        # return index of key before change to int
        #data = int(self.str_decode(data))
        data = self.int_decode(data)

        return data

    def save(self, geodata: BasicGeoData):
        """
        Save the sample to the database.
        :param geodata:
        :return:
        """
        key = self.sample_number_to_key(self.num_sample)

        self._save_index(geodata.header, key)

        self._save_header(geodata.header, key)
        self._save_data(geodata.data, key)
        self._save_target(geodata.target, key)

        self.num_sample += 1
        self._write_num_sample(self.num_sample)

    def fetch_num_sample(self):
        """
        get the number of sample in the database from the saved db entry
        :return:
        """
        with self._lmdb_env.begin(write=True, db=self.meta_db) as txn:
            msg = txn.get(self.num_sample_key, default=self.int_encode(0))

        return self.int_decode(msg)

    def _write_num_sample(self, num_sample: int):
        """
        Write the number of sample into the db
        :param num_sample:
        :return:
        """
        msg = self.int_encode(num_sample)
        with self._lmdb_env.begin(write=True, db=self.meta_db) as txn:
            txn.put(self.num_sample_key, msg)

    def _save_index(self, geo_header: GeoDataHeader, key: int):
        """
        Save the file index i.e. the number linked to a header
        :param geo_header:
        :param key:
        :return:
        """
        index_key = self.header_to_index_key(geo_header)

        with self._lmdb_env.begin(write=True, db=self.index_db) as txn:
            txn.put(index_key, key)

    def _save_header(self, geo_header: GeoDataHeader, key: int):
        """
        Save only the header to the db (function called by write)
        :param geo_header:
        :param key:
        :return:
        """
        data = self.header_serializer.serialize(geo_header)

        with self._lmdb_env.begin(write=True, db=self.header_db) as txn:
            txn.put(key, data)

    def _save_data(self, geodata: BasicGeoData, key: int):
        """
        Save only the input part to the db (function called by write)
        :param geodata:
        :param key:
        :return:
        """
        data = self.data_serializer.serialize(geodata)

        with self._lmdb_env.begin(write=True, db=self.data_db) as txn:
            txn.put(key, data)

    def _save_target(self, geodata: BasicGeoData, key: int):
        """
        Save only the output part to the db (function called by write)
        :param geodata:
        :param key:
        :return:
        """
        data = self.data_serializer.serialize(geodata)

        with self._lmdb_env.begin(write=True, db=self.category_db) as txn:
            txn.put(key, data)

    def open(self):
        """Open the db for transaction"""
        # Open LMDB environment

        self._lmdb_env = lmdb.open(self.db_path, map_size=self.map_size_limit, max_dbs=self.num_db)

        self.index_db = self._lmdb_env.open_db(self.index_db_name)
        self.meta_db = self._lmdb_env.open_db(self.meta_db_name)
        self.header_db = self._lmdb_env.open_db(self.header_db_name)
        self.data_db = self._lmdb_env.open_db(self.input_db_name)
        self.category_db = self._lmdb_env.open_db(self.output_db_name)

        self.num_sample = self.fetch_num_sample()

    def close(self):
        """Close the db"""
        self._lmdb_env.close()

    def __len__(self):
        """Return the number of sample in the database
        :return:
        """
        return self.num_sample

    # Stores geospatial training data in LMDB format with the following structure:
    #     - index_db: Maps (filename, feature_id) to sample keys
    #     - meta_db: Stores metadata (total samples, samples per category, etc.)
    #     - header_db: MessagePack-serialized headers (geometry, source file, source ID)
    #     - data_db: Raster data matrices
    #     - out_db: Target outputs/categories

class LMDBKeepENVDAO(LMDBasicGeoDataDAO):
    """LMDB DAO that keeps the environment open for performance.

    Unlike the base class which opens/closes the environment on each transaction,
    this variant keeps the LMDB environment open throughout its lifetime for
    improved performance in read-heavy workloads.

    Warning:
        Must be properly closed to avoid resource leaks.
    """

    def __init__(self, db_path, map_size_limit=int(1e+11), header_serializer=None, data_serializer=None):
        super().__init__(db_path, map_size_limit, header_serializer, data_serializer)
        self._lmdb_env = lmdb.open(self.db_path, map_size=self.map_size_limit, max_dbs=self.num_db)

        self.index_db = self._lmdb_env.open_db(self.index_db_name)
        self.meta_db = self._lmdb_env.open_db(self.meta_db_name)
        self.header_db = self._lmdb_env.open_db(self.header_db_name)
        self.data_db = self._lmdb_env.open_db(self.input_db_name)
        self.category_db = self._lmdb_env.open_db(self.output_db_name)

        self.num_sample = self.fetch_num_sample()
    def open(self):
        """Open the db for transaction"""
        # Open LMDB environment
        pass

    # Stores geospatial training data in LMDB format with the following structure:
    #     - index_db: Maps (filename, feature_id) to sample keys
    #     - meta_db: Stores metadata (total samples, samples per category, etc.)
    #     - header_db: MessagePack-serialized headers (geometry, source file, source ID)
    #     - data_db: Raster data matrices
    #     - out_db: Target outputs/categories

    def close(self):
        """Close the db"""
        pass

class LMDBReader(GeoDataReader):
    """High-level reader for LMDB geospatial databases.

    Attributes:
        db_path: Path to LMDB database.
        header_serializer: Optional custom header serializer.
        data_serializer: Optional custom data serializer.
        keep_env_open: Whether to keep LMDB environment open.
    """

    def __init__(self, db_path, header_serializer=None, data_serializer=None, keep_env_open=False):

        if keep_env_open:
            super().__init__(LMDBKeepENVDAO(db_path,
                                            header_serializer=header_serializer,
                                            data_serializer=data_serializer))
        else:
            super().__init__(LMDBasicGeoDataDAO(db_path,
                                                header_serializer=header_serializer,
                                                data_serializer=data_serializer))

class LMDBWriter(GeoDataWriter):
    """High-level writer for LMDB geospatial databases.

    Attributes:
        db_path: Path to LMDB database.
        header_serializer: Optional custom header serializer.
        data_serializer: Optional custom data serializer.
        keep_env_open: Whether to keep LMDB environment open.
    """

    def __init__(self, db_path, header_serializer=None, data_serializer=None, keep_env_open=False):

        if keep_env_open:
            super().__init__(LMDBKeepENVDAO(db_path,
                                            header_serializer=header_serializer,
                                            data_serializer=data_serializer))
        else:
            super().__init__(LMDBasicGeoDataDAO(db_path,
                                                header_serializer=header_serializer,
                                                data_serializer=data_serializer))



