from redis_work_queue import Item
from redis import Redis
from constants.redis_queue import REDIS_HOST, backend_fail_queue, backend_2_process_queue, backend_3_output_queue
from constants.output_dirs import OUTPUT_DIR_CLASS_FITS
from constants.mongo import COLLECTION_CLASS_FITS
from helpers.download import download_file_from_file_server
from model.model_handcrafted_v2 import process_abundance_h_v2


db = Redis(host=REDIS_HOST)


def run_checker():
    while True:
        print("Waiting for job ...")
        job: Item = backend_2_process_queue.lease(db, 5)  # type: ignore
        try:
            doc = job.data_json()
            print(f"starting {doc}")

            output_file_path = f"{OUTPUT_DIR_CLASS_FITS}/{doc["_id"]}.fits"

            success = download_file_from_file_server(
                {
                    "_id": doc["_id"],
                    "path": output_file_path,
                },
                COLLECTION_CLASS_FITS,
                OUTPUT_DIR_CLASS_FITS,
            )

            if not success:
                print("download failed")
                item = Item.from_json_data({"_id": doc["_id"], "stage": "PROCESS"})
                backend_fail_queue.add_item(db, item)
                continue

            results = process_abundance_h_v2(output_file_path)
            results["_id"] = doc["_id"]
            results_item = Item.from_json_data(id=job.id, data=results)
            backend_3_output_queue.add_item(db, results_item)

        except Exception:
            import traceback

            print(traceback.format_exc())
        finally:
            backend_2_process_queue.complete(db, job)


if __name__ == "__main__":
    run_checker()
