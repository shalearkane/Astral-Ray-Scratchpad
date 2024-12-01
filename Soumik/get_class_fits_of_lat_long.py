from pymongo import MongoClient

from constants.class_fits import (
    V0_LAT,
    V0_LON,
    V1_LAT,
    V1_LON,
    V2_LAT,
    V2_LON,
    V3_LAT,
    V3_LON,
)
from plot.land_patches import plot_quadrilaterals
from constants.mongo import (
    MONGO_URI,
    DATABASE_ISRO,
    COLLECTION_CLASS_FITS_ACCEPTED,
)
from constants.misc import FILE_SERVER
import requests
from typing import List, Tuple, Optional


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
    list_of_docs = get_class_file(20, 130)
    list_of_land_patches: List[List[Tuple[float, float]]] = list()
    for doc in list_of_docs:
        list_of_land_patches.append(
            [
                (doc[V0_LAT], doc[V0_LON]),
                (doc[V1_LAT], doc[V1_LON]),
                (doc[V2_LAT], doc[V2_LON]),
                (doc[V3_LAT], doc[V3_LON]),
            ]
        )
        download_file(doc)

    plot_quadrilaterals(list_of_land_patches, None, 0.05)
