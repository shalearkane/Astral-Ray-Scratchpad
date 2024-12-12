from redis_work_queue import Item
from redis import Redis
from constants.redis_queue import (
    REDIS_HOST,
    backend_0_fail_queue,
    backend_2_xrf_line_queue,
    backend_3_prediction_queue,
    backend_4_x2_abund_compare_queue,
    step2_xrf_line_intensity_job_queue,
    backend_5_sr_process_queue,
)
from constants.output_dirs import OUTPUT_DIR_JOB_FITS
from constants.mongo import COLLECTION_CLASS_JOB
from helpers.download import download_file_from_file_server
from model.model_handcrafted_v3 import process_abundance_h_v3


db = Redis(host=REDIS_HOST)


def run_checker():
    while True:
        print("Waiting for job ...")
        job: Item = backend_2_xrf_line_queue.lease(db, 5)  # type: ignore
        try:
            doc = job.data_json()
            print(f"starting {doc}")

            output_file_path = f"{OUTPUT_DIR_JOB_FITS}/{job.id()}.fits"

            success = download_file_from_file_server(
                {
                    "_id": job.id(),
                    "path": output_file_path,
                },
                COLLECTION_CLASS_JOB,
                OUTPUT_DIR_JOB_FITS,
            )

            if not success:
                print("download failed")
                item = Item.from_json_data({"_id": job.id(), "stage": "PROCESS"})
                backend_0_fail_queue.add_item(db, item)
                continue

            results = process_abundance_h_v3(output_file_path, True)
            results["clientId"] = doc["clientId"]
            results_item = Item.from_json_data(id=job.id(), data=results)

            with open("redis-abundance.json", "w") as f:
                import json

                f.write(json.dumps(results))

            backend_3_prediction_queue.add_item(db, results_item)
            backend_4_x2_abund_compare_queue.add_item(db, results_item)
            step2_xrf_line_intensity_job_queue.add_item(db, results_item)

            sr_input = Item.from_json_data(id=job.id(), data={"clientId": doc["clientId"], "lat": 23.0, "lon": 24})
            backend_5_sr_process_queue.add_item(db, sr_input)

        except Exception:
            import traceback

            print(traceback.format_exc())
        finally:
            backend_2_xrf_line_queue.complete(db, job)


if __name__ == "__main__":
    run_checker()
