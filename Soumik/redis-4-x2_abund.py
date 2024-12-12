from redis_work_queue import Item
from redis import Redis
from model.model_generic import process_abundance_x2
from constants.output_dirs import OUTPUT_DIR_JOB_FITS
from constants.mongo import COLLECTION_CLASS_JOB
from constants.redis_queue import REDIS_HOST, backend_4_x2_abund_compare_queue, step4_x2_abund_job_queue

from helpers.download import download_file_from_file_server
from os.path import join

db = Redis(host=REDIS_HOST)
background = "model/data/reference/background_allevents.fits"
solar = "data-generated/client/some.txt"
scatter_atable = "data-generated/client/some.fits"


def run_checker():
    while True:
        print("Waiting for job ...")
        job: Item = backend_4_x2_abund_compare_queue.lease(db, 5)  # type: ignore
        try:
            input = job.data_json()
            print(f"starting on {input}")
            print(job.id())

            success = download_file_from_file_server(
                {"_id": job.id(), "path": f"{job.id()}.fits"},
                COLLECTION_CLASS_JOB,
                OUTPUT_DIR_JOB_FITS,
            )

            if not success:
                print("could not download file")
                raise Exception("could not download file")

            class_l1 = join(OUTPUT_DIR_JOB_FITS, f"{job.id()}.fits")

            x2_abund_output = process_abundance_x2(class_l1, background, solar, scatter_atable)
            stage_output = {
                "clientId": input["cliendId"],
                "wt": {
                    "na": x2_abund_output["wt"]["Wt_Na"],
                    "mg": x2_abund_output["wt"]["Wt_Mg"],
                    "al": x2_abund_output["wt"]["Wt_Al"],
                    "si": x2_abund_output["wt"]["Wt_Si"],
                    "ca": x2_abund_output["wt"]["Wt_Ca"],
                    "ti": x2_abund_output["wt"]["Wt_Ti"],
                    "fe": x2_abund_output["wt"]["Wt_Fe"],
                    "o": x2_abund_output["wt"]["Wt_O"],
                },
                "error": {
                    "na": x2_abund_output["error"]["Wt_Na"],
                    "mg": x2_abund_output["error"]["Wt_Mg"],
                    "al": x2_abund_output["error"]["Wt_Al"],
                    "si": x2_abund_output["error"]["Wt_Si"],
                    "ca": x2_abund_output["error"]["Wt_Ca"],
                    "ti": x2_abund_output["error"]["Wt_Ti"],
                    "fe": x2_abund_output["error"]["Wt_Fe"],
                    "o": x2_abund_output["error"]["Wt_O"],
                },
            }

            stage_output_item = Item.from_json_data(id=job.id(), data=stage_output)
            step4_x2_abund_job_queue.add_item(db, stage_output_item)

        except Exception:
            import traceback

            print(traceback.format_exc())
        finally:
            backend_4_x2_abund_compare_queue.complete(db, job)


if __name__ == "__main__":
    run_checker()
