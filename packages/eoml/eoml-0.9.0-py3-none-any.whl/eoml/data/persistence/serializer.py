"""MessagePack-based serializers for geospatial data and headers.

This module provides efficient binary serialization using MessagePack format
for geospatial dataset headers and numpy array data. MessagePack offers compact
representation and fast serialization/deserialization, making it ideal for
high-performance machine learning pipelines.

Geometries are serialized as WKT (Well-Known Text) strings for portability
and ease of reconstruction.
"""

import msgpack
import numpy as np
import shapely
import shapely.wkt

from eoml.data.basic_geo_data import GeoDataHeader
from eoml.data.persistence.generic import GeoDataHeaderSerializer, GeoDataSerializer


class MsgpackGeoDataHeaderSerializer(GeoDataHeaderSerializer):
    """MessagePack serializer for GeoDataHeader objects.

    Serializes geospatial sample headers including geometry (as WKT),
    source file information, and sample identifiers.
    """
    def decode_geodata_header(self, obj):
        """
        if the field __header__ is in the obj to deserialize, create a GeodataHeader from the dic
        """
        if '__header__' in obj:
            obj = GeoDataHeader(obj["id"], shapely.wkt.loads(obj["geometry"]), obj["file_name"])
        return obj

    def encode_geodata_header(self, obj):
        """
        transform the header to a dictionary of known type and add a field to recognise the type
        """
        if isinstance(obj, GeoDataHeader):
            return {'__header__': True,
                    "id": obj.idx,
                    "geometry": obj.geometry.wkt,
                    "file_name": obj.file_name.stem}
        return obj

    def serialize(self, header) -> bytes:
        return msgpack.packb(header, default=self.encode_geodata_header, use_bin_type=True)

    def deserialize(self, msg):
        return msgpack.unpackb(msg, object_hook=self.decode_geodata_header, raw=False)


class MsgpackGeoDataSerializer(GeoDataSerializer):
    """MessagePack serializer for numpy array data.

    Efficiently serializes numpy arrays by storing dtype, shape, and raw bytes,
    enabling fast reconstruction without data loss.
    """
    def encode_geodata(self, obj):
        """
        Assum the data are a numpy array. Save it to bytes adding info about type and shape to reconstruct it
        """
        if isinstance(obj, np.ndarray):
            return {'__array__': True,
                    "dtype": obj.dtype.str,
                    "shape": obj.shape,
                    "data": obj.tobytes()}
        return obj

    def decode_geodata(self, obj):
        """
        Reconstruct numpy array
        """
        if '__array__' in obj:
            obj = np.frombuffer(obj["data"], dtype=np.dtype(obj["dtype"])).reshape(obj["shape"])
        return obj

    def serialize(self, data)-> bytes:
        return msgpack.packb(data, default=self.encode_geodata, use_bin_type=True)

    def deserialize(self, msg):
        return msgpack.unpackb(msg, object_hook=self.decode_geodata, raw=False)