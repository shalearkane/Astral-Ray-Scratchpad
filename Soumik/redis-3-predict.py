from typing import Any, Dict
from redis_work_queue import Item
from redis import Redis
from ML.modular_predict_abundancies_v1 import abundance_prediction
from helpers.combine_fits_with_metadata import get_latitude_longitude_from_hdul, hdul_meta_to_dict, process_hdul
from constants.mongo import COLLECTION_CLASS_JOB
from constants.redis_queue import REDIS_HOST, backend_3_prediction_queue, step3_ml_prediction_job_queue

from helpers.download import stream_file_from_file_server
from helpers.visual_peak import generate_visible_peaks

from astropy.io import fits
from io import BytesIO

db = Redis(host=REDIS_HOST)


def run_checker():
    while True:
        print("Waiting for job ...")
        job: Item = backend_3_prediction_queue.lease(db, 5)  # type: ignore
        try:
            abundance_dict = job.data_json()
            abundance_dict.pop("fitting")
            print(abundance_dict)
            print(f"starting {abundance_dict}")
            print(job.id())

            success, fits_bytes = stream_file_from_file_server(
                {
                    "_id": job.id(),
                },
                COLLECTION_CLASS_JOB,
            )

            with fits.open(BytesIO(fits_bytes)) as hdul:
                visible_peaks = generate_visible_peaks(hdul)
                latitude, longitude = get_latitude_longitude_from_hdul(hdul)
                computed_metadata = process_hdul(hdul, {"visible_peaks": visible_peaks}, 1, method="average")

                prediction_input: Dict[str, Any] = {
                    "wt": abundance_dict["intensity"],
                    "chi_2": abundance_dict["chi_2"],
                    "dof": abundance_dict["dof"],
                    "photon_count": int(computed_metadata.photon_counts.sum()),
                    "computed_metadata": hdul_meta_to_dict(computed_metadata),
                    "latitude": latitude,
                    "longitude": longitude,
                }

                prediction_output = abundance_prediction(prediction_input)
                print(f"prediction output: {prediction_output}")
                next_stage_input = {
                    "clientId": abundance_dict["clientId"],
                    "wt": {
                        "mg": prediction_output["model_mg_prediction"],
                        "al": prediction_output["model_al_prediction"],
                        "si": prediction_output["model_si_prediction"],
                        "fe": prediction_output["model_fe_prediction"],
                    },
                }

                next_stage_item = Item.from_json_data(id=job.id(), data=next_stage_input)
                step3_ml_prediction_job_queue.add_item(db, next_stage_item)

        except Exception:
            import traceback

            print(traceback.format_exc())
        finally:
            backend_3_prediction_queue.complete(db, job)


if __name__ == "__main__":
    run_checker()
