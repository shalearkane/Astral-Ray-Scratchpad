from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor
import concurrent
from datetime import datetime, timezone
from pymongo import MongoClient
from itertools import batched

from criterion.illumination import check_if_illuminated
from constants.class_fits import *
from constants.mongo import *
from constants.misc import *

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
class_fits_all = db[COLLECTION_CLASS_FITS]
class_fits_accepted= db[COLLECTION_CLASS_FITS_ACCEPTED]

fits_passed: int = 0
fits_failed: int = 0
count: int = 0


# Define the processing function for each document
def process_document(doc):
    if "-" in doc[STARTIME]:
        start_time = datetime.strptime(doc[STARTIME], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
        end_time = datetime.strptime(doc[ENDTIME], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
    else:
        start_time = datetime.strptime(doc[STARTIME], "%Y%m%dT%H%M%S%f").replace(tzinfo=timezone.utc)
        end_time = datetime.strptime(doc[ENDTIME], "%Y%m%dT%H%M%S%f").replace(tzinfo=timezone.utc)

    a: bool = check_if_illuminated(doc[V0_LAT], doc[V0_LON], start_time)
    b: bool = check_if_illuminated(doc[V1_LAT], doc[V1_LON], end_time)


    with open(STATISTICS_COMM_PIPE, 'w') as pipe:
        if a and b:
            pipe.write("1\n")
        else:
            pipe.write("0\n")


cursor = class_fits_all.find().batch_size(1000).limit(1000)


with ProcessPoolExecutor() as executor:
    for batch in batched(cursor, 50):
        future_to_doc = {executor.submit(process_document, doc): doc for doc in batch}
        concurrent.futures.wait(future_to_doc, timeout=None, return_when=ALL_COMPLETED)
