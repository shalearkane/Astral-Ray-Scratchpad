from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime, timezone
from pymongo import MongoClient
from itertools import batched
from bson import ObjectId
import traceback

from criterion.illumination import check_if_illuminated
from criterion.geotail import check_if_not_in_geotail
from constants.class_fits import *
from constants.mongo import *
from constants.misc import *

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
class_fits_all = db[COLLECTION_CLASS_FITS]

fits_passed: int = 0
fits_failed: int = 0
count: int = 0


def create_or_update_document(doc: dict, check_passed: bool):
    class_fits_accepted = MongoClient(MONGO_URI)[DATABASE_NAME][
        COLLECTION_CLASS_FITS_ACCEPTED
    ]

    if class_fits_accepted.find_one(filter={"_id": ObjectId(doc["_id"])}) is None:
        doc["passed_check"] = check_passed
        doc["_id"] = ObjectId(doc["_id"])
        class_fits_accepted.insert_one(doc)
    else:
        class_fits_accepted.find_one_and_update(
            filter={"_id": ObjectId(doc["_id"])},
            update={"$set": {"passed_check": check_passed}},
        )


# Define the processing function for each document
def process_document(doc: dict):
    try:

        if "-" in doc[STARTIME]:
            start_time = datetime.strptime(doc[STARTIME], "%Y-%m-%dT%H:%M:%S.%f")
            end_time = datetime.strptime(doc[ENDTIME], "%Y-%m-%dT%H:%M:%S.%f")
        else:
            start_time = datetime.strptime(doc[STARTIME], "%Y%m%dT%H%M%S%f")
            end_time = datetime.strptime(doc[ENDTIME], "%Y%m%dT%H%M%S%f")

        start_time = start_time.replace(tzinfo=timezone.utc)
        end_time = start_time.replace(tzinfo=timezone.utc)

        a: bool = check_if_illuminated(doc[V0_LAT], doc[V0_LON], start_time)
        b: bool = check_if_illuminated(doc[V2_LAT], doc[V2_LON], end_time)

        c: bool = check_if_not_in_geotail(start_time)
        d: bool = check_if_not_in_geotail(end_time)

        with open(STATISTICS_COMM_PIPE, "w") as pipe:
            if a and b and c and d:
                pipe.write("1\n")
                create_or_update_document(doc, True)
            else:
                pipe.write("0\n")

            pipe.flush()
    except Exception:
        print(doc["_id"])
        print(traceback.format_exc())


cursor = class_fits_all.find().batch_size(1000).limit(1000000)

count = 0

# for doc in cursor:
#     count += 1
#     process_document(doc)

with ProcessPoolExecutor() as executor:
    for batch in batched(cursor, 50):
        future_to_doc = {executor.submit(process_document, doc): doc for doc in batch}
        count += len(future_to_doc)
        wait(future_to_doc, timeout=None, return_when=ALL_COMPLETED)

print(f"Processed {count} documents")
