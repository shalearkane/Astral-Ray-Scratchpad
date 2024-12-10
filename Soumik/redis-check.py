from typing import Dict, List
from redis_work_queue import Item
from redis import Redis
from helpers.fits_get_plot import get_fits_plot
from helpers.utilities import to_datetime_t
from constants.output_dirs import OUTPUT_DIR_JOB_FITS
from constants.mongo import COLLECTION_CLASS_JOB
from constants.redis_queue import (
    REDIS_HOST,
    backend_fail_queue,
    backend_2_process_queue,
    backend_1_check_queue,
    step1_checks_job_queue,
    create_job_queue,
)

from helpers.download import stream_file_from_file_server
from helpers.visual_peak import generate_visible_peaks, element_kalpha_lines
from criterion.photon_count import photon_count_from_hdul
from criterion.geotail import check_if_not_in_geotail

from astropy.io import fits
from io import BytesIO

db = Redis(host=REDIS_HOST)


def run_checker():
    while True:
        print("Waiting for job ...")
        job: Item = create_job_queue.lease(db, 5)  # type: ignore
        try:
            doc = job.data_json()
            print(f"starting {doc}")
            print(job.id())

            success, fits_bytes = stream_file_from_file_server(
                {
                    "_id": job.id(),
                    "path": f"{OUTPUT_DIR_JOB_FITS}/{job.id()}.fits",
                },
                COLLECTION_CLASS_JOB,
            )

            # if not success:
            #     print("download failed")
            #     item = Item.from_json_data({"_id": doc["_id"], "stage": "CHECK"})
            #     backend_fail_queue.add_item(db, item)
            #     continue

            with fits.open(BytesIO(fits_bytes)) as hdul:
                print("checking ...")
                metadata = hdul[1].header  # type: ignore
                start_time = to_datetime_t(metadata["STARTIME"])
                end_time = to_datetime_t(metadata["ENDTIME"])

                not_in_geotail = check_if_not_in_geotail(start_time) and check_if_not_in_geotail(end_time)
                photon_count = photon_count_from_hdul(hdul)
                visible_peaks = generate_visible_peaks(hdul)
                si_visible_peak = "si" in visible_peaks.keys()
                peaks: Dict[str, List[Dict[str, float]]] = dict()

                for key, val in visible_peaks.items():
                    if key not in peaks.keys():
                        peaks[key] = list()

                    peaks[key].append({"channelNumber": int(element_kalpha_lines[key] / 0.01361), "count": float(val)})

                next_stage_input = {
                    "clientId": doc["clientId"],
                    "geotail": not not_in_geotail,
                    "photonCount": photon_count,
                    "siVisiblePeak": si_visible_peak,
                    "fitsPlot": get_fits_plot(hdul),
                    "peaks": peaks,
                }

                print(next_stage_input)
                with open("redis-check.json", "w") as f:
                    import json

                    f.write(json.dumps(next_stage_input))

                if not_in_geotail and si_visible_peak:
                    print("accepted")
                    doc_item = Item.from_json_data(id=job.id(), data=next_stage_input)
                    backend_2_process_queue.add_item(db, doc_item)
                    step1_checks_job_queue.add_item(db, doc_item)
                else:
                    print("rejected")

        except Exception:
            import traceback

            print(traceback.format_exc())
        finally:
            backend_1_check_queue.complete(db, job)


if __name__ == "__main__":
    run_checker()
