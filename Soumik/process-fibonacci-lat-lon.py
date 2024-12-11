import multiprocessing
from typing import Any, Dict, List, Set, Tuple


from helpers.combine_fits_with_metadata import combine_fits_with_meta, hdul_meta_to_dict
from model.model_handcrafted_v2 import process_abundance_h_v2
from constants.output_dirs import OUTPUT_DIR_CLASS_FITS, OUTPUT_DIR_COMBINED_FITS
from constants.mongo import COLLECTION_CLASS_FITS, COLLECTION_FIBONACCI_LAT_LON_V2, DATABASE_ISRO, MONGO_URI, COLLECTION_DATA_COLLECTION_V4
from helpers.download import download_file_from_file_server
from helpers.query_class import get_class_fits_at_lat_lon
from os.path import isfile
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Final
from time import sleep

NUM_PROCESSES: Final[int] = 8


def save_to_mongo(latitude: str, longitude: str, doc: Dict[str, Any], fibonacci_collection: Collection):
    fibonacci_collection.find_one_and_update({"latitude": latitude, "longitude": longitude}, {"$set": doc})


def get_job_from_mongo(fibonacci_collection: Collection) -> Tuple[str, str]:
    one_job = fibonacci_collection.find_one_and_update(
        {"status": False},
        {
            "$set": {"status": True},
            "$currentDate": {"last_served": True},
        },
        return_document=True,
    )

    return one_job["latitude"], one_job["longitude"]


def generate_combined_fits_for_lat_lon(worker_id: int, redo: bool):
    data_collection = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_DATA_COLLECTION_V4]

    while True:
        latitude_str, longitude_str = get_job_from_mongo(data_collection)

        print(f"{latitude_str} - {longitude_str}")

        try:
            combined_fits_filename = f"{latitude_str}_{longitude_str}.fits"
            combined_fits_path = f"{OUTPUT_DIR_COMBINED_FITS}/{combined_fits_filename}"
            if not redo and isfile(combined_fits_path):
                print(f"already generated: {combined_fits_path}")

            docs = get_class_fits_at_lat_lon(float(latitude_str), float(longitude_str))

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
                abundance_dict = process_abundance_h_v2(combined_fits_path)

                mongo_doc: Dict[str, Any] = {
                    "wt": abundance_dict["wt"],
                    "chi_2": abundance_dict["chi_2"],
                    "dof": abundance_dict["dof"],
                    "photon_count": int(computed_metadata.photon_counts.sum()),
                    "computed_metadata": hdul_meta_to_dict(computed_metadata),
                    "status": True,
                }

                save_to_mongo(latitude_str, longitude_str, mongo_doc, data_collection)
            else:
                print(f"could not generate: {combined_fits_path}")
        except Exception:
            import traceback

            print(traceback.format_exc())


def monitor_workers():
    """
    Monitor and maintain the pool of workers.
    Restarts a worker if it dies.
    """
    workers = {}
    try:
        while True:
            # Spin up workers until NUM_PROCESSES are running
            for i in range(NUM_PROCESSES):
                if i not in workers or not workers[i].is_alive():
                    # Start a new worker
                    print(f"Starting/restarting worker {i}.")
                    worker_process = multiprocessing.Process(target=generate_combined_fits_for_lat_lon, args=(i, True))
                    worker_process.start()
                    workers[i] = worker_process

            sleep(10)
            # Check worker statuses

    except KeyboardInterrupt:
        print("Shutting down server...")
        for proc in workers.values():
            proc.kill()
        print("All workers terminated.")


if __name__ == "__main__":
    # do_in_parallel()
    monitor_workers()
    # generate_combined_fits_for_lat_lon(1, True)
