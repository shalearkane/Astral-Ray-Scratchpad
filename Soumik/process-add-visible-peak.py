from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor, wait
from typing import Dict, Tuple
from pymongo import MongoClient, collection

from itertools import batched
from bson import ObjectId
from astropy.io import fits

from helpers.visible_peak import generate_visible_peaks
from helpers.download import stream_file_from_file_server
from constants.mongo import (
    COLLECTION_CLASS_FITS,
    MONGO_URI,
    DATABASE_ISRO,
)
from io import BytesIO

class_fits_all = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS]
cursor = class_fits_all.find({"photon_count": {"$gte": 3000}}).batch_size(24000)
count = 0


def set_visible_peaks_count(_id: ObjectId, visible_peaks: Dict[str, float], class_fits: collection.Collection):
    class_fits.find_one_and_update({"_id": _id}, {"$set": {"visible_peaks": visible_peaks}})


def batched_process_document_for_setting_photon_count(docs: Tuple[dict]):
    try:
        class_fits = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS]

        for doc in docs:
            success, fits_bytes = stream_file_from_file_server(doc, COLLECTION_CLASS_FITS)

            if success:
                with fits.open(BytesIO(fits_bytes)) as hdul:
                    visible_peaks = generate_visible_peaks(hdul)
                    set_visible_peaks_count(ObjectId(doc["_id"]), visible_peaks, class_fits)

    except Exception:
        from traceback import format_exc

        print(doc["_id"])
        print(format_exc())


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
