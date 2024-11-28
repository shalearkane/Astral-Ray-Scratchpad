from pymongo import MongoClient, DESCENDING
import pandas as pd

from typing import Tuple
from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor, wait
from itertools import batched
from constants.mongo import (
    MONGO_URI,
    DATABASE_ISRO,
    COLLECTION_CLASS_FITS_ACCEPTED,
)
from constants.misc import STATISTICS_COMM_PIPE, FILE_SERVER
from datetime import datetime
import requests


def get_class_file(lat: float, lon: float):
    class_fits_accepted = MongoClient(MONGO_URI)[DATABASE_ISRO][
        COLLECTION_CLASS_FITS_ACCEPTED
    ]
    lon_r = lon - 360.0

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


def download_file(doc: dict):
    response = requests.get(f"{FILE_SERVER}/primary/{doc["_id"]}")
    response.raise_for_status()

    with open(f"data/class/{doc["path"].split("/")[-1]}", "wb") as f:
        f.write(response.content)


if __name__ == "__main__":
    l = get_class_file(20, 130)
    for ll in l:
        download_file(ll)
