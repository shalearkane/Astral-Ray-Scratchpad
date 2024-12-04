from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor, wait
from itertools import batched
from pymongo.collection import Collection
from scripts.get_intersections import calculate_intersections, read_csv_to_polygons
from typing import Any, Optional, Tuple, Dict
from pymongo import MongoClient

from constants.mongo import COLLECTION_CLASS_FITS_TEST_FITS, DATABASE_ISRO, MONGO_URI

true_abundance = read_csv_to_polygons("data/isro/elemental_abundances_by_isro.csv")


def batch_process_docs_to_assign_true_abundances(docs: Tuple[Dict[str, Any], ...], test_fits: Optional[Collection] = None):
    if test_fits is None:
        test_fits = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS_TEST_FITS]

    for doc in docs:
        true_stuff = calculate_intersections(true_abundance, doc)
        if true_stuff:
            true_stuff["INTRSCTN_P"] = True
            test_fits.find_one_and_update({"path": doc["path"]}, {"$set": true_stuff})
        else:
            test_fits.find_one_and_update({"path": doc["path"]}, {"$set": {"INTRSCTN_P": True}})


class_fits_test_fits = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS_TEST_FITS]
cursor = class_fits_test_fits.find({"INTRSCTN_P": {"$exists": False}}).batch_size(24000)
count = 0

# for doc in cursor:
#     count += 1
#     doc = (doc, doc)
#     class_fits_flare_classified = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_CLASS_FITS_TEST_FITS]
#     batch_process_docs_to_assign_true_abundances(doc, class_fits_flare_classified)

with ProcessPoolExecutor() as executor:
    for batches in batched(cursor, 24000):
        future_to_doc = {executor.submit(batch_process_docs_to_assign_true_abundances, batch): batch for batch in batched(batches, 1500)}
        wait(future_to_doc, timeout=None, return_when=ALL_COMPLETED)

        count += 24000
        print(count)

print(f"Processed {count} documents")
