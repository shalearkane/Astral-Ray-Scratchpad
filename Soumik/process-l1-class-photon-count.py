from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor, wait
from typing import Tuple
from pymongo import MongoClient, collection

from itertools import batched
from bson import ObjectId
from astropy.io import fits

from constants.output_dirs import OUTPUT_DIR_TMP
from criterion.photon_count import photon_count_from_hdul
from helpers.download import download_file_from_file_server
from constants.mongo import (
    COLLECTION_CLASS_FITS,
    MONGO_URI,
    DATABASE_ISRO,
)
import os


def set_photon_count(_id: ObjectId, photon_count: int, class_fits: collection.Collection):
    class_fits.find_one_and_update({"_id": _id}, {"$set": {"photon_count": photon_count}})


def batched_process_document_for_setting_photon_count(docs: Tuple[dict]):
    try:
        class_fits = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS]

        for doc in docs:
            if download_file_from_file_server(doc, COLLECTION_CLASS_FITS, OUTPUT_DIR_TMP):
                on_disk_path = os.path.join(OUTPUT_DIR_TMP, doc["path"].split("/")[-1])

                with fits.open(on_disk_path) as hdul:
                    photon_count = photon_count_from_hdul(hdul)
                    set_photon_count(ObjectId(doc["_id"]), photon_count, class_fits)

                os.remove(on_disk_path)

    except Exception:
        from traceback import format_exc

        print(doc["_id"])
        print(format_exc())


class_fits_all = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS]
cursor = class_fits_all.find({"photon_count": {"$exists": False}}).batch_size(24000)
count = 0

# for doc in cursor:
#     count += 1
#     class_fits_flare_classified = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS_FLARE_CLASSIFIED]
#     process_document_for_flare_class(doc, class_fits_flare_classified)

with ProcessPoolExecutor() as executor:
    for batches in batched(cursor, 24000):
        future_to_doc = {executor.submit(batched_process_document_for_setting_photon_count, batch): batch for batch in batched(batches, 1500)}
        wait(future_to_doc, timeout=None, return_when=ALL_COMPLETED)

        count += 24000
        print(count)

print(f"Processed {count} documents")
