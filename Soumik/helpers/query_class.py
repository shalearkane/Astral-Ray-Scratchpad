from typing import Any, List, Tuple, Dict
from constants.output_dirs import OUTPUT_DIR_CLASS_FITS
from helpers.download import download_file_from_file_server
from constants.class_fits import V0_LAT, V0_LON, V1_LAT, V1_LON, V2_LAT, V2_LON, V3_LAT, V3_LON
from constants.mongo import (
    COLLECTION_CLASS_FITS,
    COLLECTION_CLASS_FITS_FLARE_CLASSIFIED,
    MONGO_URI,
    DATABASE_ISRO,
    COLLECTION_CLASS_FITS_ACCEPTED,
)

from pymongo import MongoClient


def get_class_fits_at_lat_lon(lat: float, lon: float) -> list[Dict[str, Any]]:
    class_fits_accepted = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS_ACCEPTED]

    filter = {
        "$and": [
            {V0_LAT: {"$gte": lat}},
            {V0_LON: {"$lte": lon}},
            {V1_LAT: {"$lte": lat}},
            {V1_LON: {"$lte": lon}},
            {V2_LAT: {"$lte": lat}},
            {V2_LON: {"$gte": lon}},
            {V3_LAT: {"$gte": lat}},
            {V3_LON: {"$gte": lon}},
            {"is_in_geotail": False},
        ]
    }

    results = class_fits_accepted.find(filter=filter)

    return [doc for doc in results]


def get_class_fits_for_flare_class(flare_class: str = "X", minimum_flare_scale: float = 0.0) -> list[Dict[str, Any]]:
    class_fits_flare_classified = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS_FLARE_CLASSIFIED]

    filter = {"flare_alphabet": flare_class, "flare_scale": {"$gte": minimum_flare_scale}}
    results = class_fits_flare_classified.find(filter)

    return [doc for doc in results]


if __name__ == "__main__":
    list_of_docs = get_class_fits_at_lat_lon(20, 130)
    list_of_land_patches: List[List[Tuple[float, float]]] = list()
    for doc in list_of_docs:
        download_file_from_file_server(doc, COLLECTION_CLASS_FITS,OUTPUT_DIR_CLASS_FITS)

        list_of_land_patches.append(
            [
                (doc[V0_LAT], doc[V0_LON]),
                (doc[V1_LAT], doc[V1_LON]),
                (doc[V2_LAT], doc[V2_LON]),
                (doc[V3_LAT], doc[V3_LON]),
            ]
        )
