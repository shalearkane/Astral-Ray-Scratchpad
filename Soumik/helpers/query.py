from constants.mongo import (
    MONGO_URI,
    DATABASE_ISRO,
    COLLECTION_CLASS_FITS_ACCEPTED,
)

from pymongo import MongoClient


def get_class_fits_at_lat_lon(lat: float, lon: float):
    class_fits_accepted = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS_ACCEPTED]

    filter = {
        "$and": [
            {"V0_LAT": {"$gte": lat}},
            {"V0_LON": {"$lte": lon}},
            {"V1_LAT": {"$lte": lat}},
            {"V1_LON": {"$lte": lon}},
            {"V2_LAT": {"$lte": lat}},
            {"V2_LON": {"$gte": lon}},
            {"V3_LAT": {"$gte": lat}},
            {"V3_LON": {"$gte": lon}},
            {"is_in_geotail": False},
        ]
    }

    result = class_fits_accepted.find(filter=filter)

    return [doc for doc in result]
