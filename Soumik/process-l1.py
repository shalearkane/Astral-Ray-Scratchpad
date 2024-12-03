from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime, timezone
from pymongo import MongoClient
from itertools import batched
from bson import ObjectId
from traceback import format_exc

import pymongo
import pymongo.collection

from criterion.illumination import check_if_illuminated
from criterion.geotail import check_if_not_in_geotail
from criterion.goes_solar_flare import get_flare_class
from constants.class_fits import *
from constants.mongo import *
from constants.misc import *


def save_accepted_document(doc: dict, check_passed: bool):
    class_fits_accepted = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS_ACCEPTED]

    # just insert
    doc[KEY_PASSED_CHECK] = check_passed
    doc["_id"] = ObjectId(doc["_id"])
    class_fits_accepted.insert_one(doc)


def save_flare_classified_document(doc: dict, collection: pymongo.collection.Collection):

    mini_doc = dict()

    mini_doc["_id"] = ObjectId(doc["_id"])
    mini_doc["start_time"] = doc["parsedStartTime"]
    mini_doc["end_time"] = doc["parsedEndTime"]
    mini_doc["path"] = doc["path"]
    mini_doc["flare_alphabet"] = doc["flare_alphabet"]
    mini_doc["flare_scale"] = doc["flare_scale"]

    mini_doc["V0_LAT"] = doc["V0_LAT"]
    mini_doc["V1_LAT"] = doc["V1_LAT"]
    mini_doc["V2_LAT"] = doc["V2_LAT"]
    mini_doc["V3_LAT"] = doc["V3_LAT"]

    mini_doc["V0_LON"] = doc["V0_LON"]
    mini_doc["V1_LON"] = doc["V1_LON"]
    mini_doc["V2_LON"] = doc["V2_LON"]
    mini_doc["V3_LON"] = doc["V3_LON"]

    mini_doc["SOLARANG"] = doc["SOLARANG"]
    mini_doc["EMISNANG"] = doc["EMISNANG"]

    collection.insert_one(mini_doc)


def process_document_for_flare_class(doc: dict, collection: pymongo.collection.Collection):
    start_time = doc["parsedStartTime"]
    end_time = doc["parsedEndTime"]

    flare_alphabet, flare_scale = get_flare_class(start_time, end_time)
    c: bool = check_if_not_in_geotail(start_time)
    d: bool = check_if_not_in_geotail(end_time)

    if c and d and flare_alphabet != "None":
        doc["flare_alphabet"] = flare_alphabet
        doc["flare_scale"] = float(flare_scale)
        save_flare_classified_document(doc, collection)


def batched_process_document_for_flare_class(docs: list[dict]):
    try:
        class_fits_flare_classified = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS_FLARE_CLASSIFIED]

        for doc in docs:
            process_document_for_flare_class(doc, class_fits_flare_classified)

    except Exception:
        print(doc["_id"])
        print(format_exc())


# Define the processing function for each document
def process_document_for_fitness(doc: dict):
    try:

        if "-" in doc[STARTIME]:
            start_time = datetime.strptime(doc[STARTIME], "%Y-%m-%dT%H:%M:%S.%f")
            end_time = datetime.strptime(doc[ENDTIME], "%Y-%m-%dT%H:%M:%S.%f")
        else:
            start_time = datetime.strptime(doc[STARTIME], "%Y%m%dT%H%M%S%f")
            end_time = datetime.strptime(doc[ENDTIME], "%Y%m%dT%H%M%S%f")

        start_time = start_time.replace(tzinfo=timezone.utc)
        end_time = end_time.replace(tzinfo=timezone.utc)

        a: bool = check_if_illuminated(doc[V0_LAT], doc[V0_LON], start_time)
        b: bool = check_if_illuminated(doc[V2_LAT], doc[V2_LON], end_time)

        c: bool = check_if_not_in_geotail(start_time)
        d: bool = check_if_not_in_geotail(end_time)

        if not c or not d:
            doc[KEY_IS_IN_GEOTAIL] = True
        else:
            doc[KEY_IS_IN_GEOTAIL] = False

        with open(STATISTICS_COMM_PIPE, "w") as pipe:
            if a and b:
                save_accepted_document(doc, True)
                pipe.write("1\n")
            else:
                pipe.write("0\n")

    except Exception:
        print(doc["_id"])
        print(format_exc())


class_fits_all = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS]
cursor = class_fits_all.find().batch_size(64000)
count = 0

# for doc in cursor:
#     count += 1
#     class_fits_flare_classified = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS_FLARE_CLASSIFIED]
#     process_document_for_flare_class(doc, class_fits_flare_classified)

with ProcessPoolExecutor() as executor:
    for batch in batched(cursor, 4000):
        future_to_doc = {executor.submit(batched_process_document_for_flare_class, doc): doc for doc in batch}
        wait(future_to_doc, timeout=None, return_when=ALL_COMPLETED)

        count += len(future_to_doc)
        print(count)

print(f"Processed {count} documents")
