from redis_work_queue import Item
from redis import Redis
from helpers.utilities import to_datetime_t
from constants.output_dirs import OUTPUT_DIR_CLASS_FITS
from constants.mongo import COLLECTION_CLASS_FITS
from constants.redis_queue import REDIS_HOST, fail_queue, process_queue, check_queue

from helpers.download import stream_file_from_file_server
from helpers.visible_peak import generate_visible_peaks
from criterion.photon_count import photon_count_from_hdul
from criterion.geotail import check_if_not_in_geotail

from astropy.io import fits
from io import BytesIO

db = Redis(host=REDIS_HOST)


def run_checker():
    while True:
        print("Waiting for job ...")
        job: Item = check_queue.lease(db, 5)  # type: ignore
        try:
            doc = job.data_json()
            print(f"starting {doc}")

            success, fits_bytes = stream_file_from_file_server(
                {
                    "_id": doc["_id"],
                    "path": f"{OUTPUT_DIR_CLASS_FITS}/{doc["_id"]}.fits",
                },
                COLLECTION_CLASS_FITS,
            )

            if not success:
                print("download failed")
                item = Item.from_json_data({"_id": doc["_id"], "stage": "CHECK"})
                fail_queue.add_item(db, item)
                continue

            with fits.open(BytesIO(fits_bytes)) as hdul:
                print("checking ...")
                metadata = hdul[1].header  # type: ignore
                start_time = to_datetime_t(metadata["STARTIME"])
                end_time = to_datetime_t(metadata["ENDTIME"])

                not_in_geotail = check_if_not_in_geotail(start_time) and check_if_not_in_geotail(end_time)
                photon_count = photon_count_from_hdul(hdul)
                si_visible_peak = "Si" in generate_visible_peaks(hdul).keys()

                print(f"{not_in_geotail} - {photon_count} - {si_visible_peak}")

                if not_in_geotail and si_visible_peak:
                    print("accepted")
                    doc_item = Item.from_json_data(doc)
                    process_queue.add_item(db, doc_item)
                else:
                    print("rejected")

        except Exception:
            import traceback

            print(traceback.format_exc())
        finally:
            check_queue.complete(db, job)


if __name__ == "__main__":
    run_checker()
