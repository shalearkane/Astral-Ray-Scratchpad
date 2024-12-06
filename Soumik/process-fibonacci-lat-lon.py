from typing import Any, Dict, List, Set, Tuple

import concurrent.futures

from helpers.combine_fits_with_metadata import combine_fits_with_meta, hdul_meta_to_dict
from model.model_handcrafted import process_abundance_h
from constants.output_dirs import OUTPUT_DIR_CLASS_FITS
from constants.mongo import COLLECTION_CLASS_FITS, COLLECTION_FIBONACCI_LAT_LON, DATABASE_ISRO, MONGO_URI
from helpers.download import download_file_from_file_server
from helpers.query_class import get_class_fits_at_lat_lon
from os.path import isfile
from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import datetime, timedelta, timezone


def save_to_mongo(latitude: str, longitude: str, doc: Dict[str, Any], fibonacci_collection: Collection):
    fibonacci_collection.find_one_and_update({"latitude": latitude, "longitude": longitude}, {"$set": doc})


def get_job_from_mongo(fibonacci_collection: Collection) -> Tuple[str, str]:
    now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(minutes=4)

    one_job = fibonacci_collection.find_one_and_update(
        {"status": False, "request_count": {"$lt": 5}, "last_served": {"$lte": time_threshold}},
        {
            "$set": {"status": True},
            "$inc": {"request_count": 1},
            "$currentDate": {"last_served": True},
        },
        return_document=True,
    )

    return one_job["latitude"], one_job["longitude"]


def generate_combined_fits_for_lat_lon(worker_id: int, redo: bool) -> bool:
    print(f"restarting worker {worker_id}")

    fibonacci_collection = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_FIBONACCI_LAT_LON]
    latitude_str, longitude_str = get_job_from_mongo(fibonacci_collection)

    print(f"{latitude_str} - {longitude_str}")

    try:
        combined_fits_filename = f"{latitude_str}_{longitude_str}.fits"
        combined_fits_path = f"{OUTPUT_DIR_CLASS_FITS}/{combined_fits_filename}"
        if not redo and isfile(combined_fits_path):
            print(f"already generated: {combined_fits_path}")
            return True

        docs = get_class_fits_at_lat_lon(float(latitude_str), float(latitude_str))

        visible_element_peaks: Set[str] = set()

        for doc in docs:
            for key in doc["visible_peaks"].keys():
                visible_element_peaks.add(key)

        file_paths: List[str] = list()
        doc_list: List[Dict[str, Any]] = list()

        for doc in docs:
            if download_file_from_file_server(doc, COLLECTION_CLASS_FITS, OUTPUT_DIR_CLASS_FITS):
                file_paths.append(f"{OUTPUT_DIR_CLASS_FITS}/{doc["path"].split("/")[-1]}")
                doc_list.append(doc)

        metadata = {"latitude": latitude_str, "longitude": longitude_str, "visible_peaks": visible_element_peaks}
        success, computed_metadata = combine_fits_with_meta(file_paths, doc_list, combined_fits_path, metadata)
        if success:
            print(f"generated: {combined_fits_path}")
            abundance_dict = process_abundance_h(combined_fits_path)

            mongo_doc: Dict[str, Any] = {
                "wt": abundance_dict["wt"],
                "chi_2": abundance_dict["chi_2"],
                "dof": abundance_dict["dof"],
                "photon_count": int(computed_metadata.photon_counts.sum()),
                "computed_metadata": hdul_meta_to_dict(computed_metadata),
                "status": True,
            }

            save_to_mongo(latitude_str, longitude_str, mongo_doc, fibonacci_collection)
            return True
        else:
            print(f"could not generate: {combined_fits_path}")
            return False
    except Exception:
        import traceback

        print(traceback.format_exc())

        return True


def do_in_parallel():
    count = 0

    with concurrent.futures.ProcessPoolExecutor() as executor:
        while True:
            try:
                future_to_doc = {executor.submit(generate_combined_fits_for_lat_lon, worker_id, False): worker_id for worker_id in range(0, 16)}
                concurrent.futures.wait(future_to_doc, timeout=None, return_when=concurrent.futures.ALL_COMPLETED)
                count += 32
                print(count)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    # do_in_parallel()
    generate_combined_fits_for_lat_lon(1, True)
