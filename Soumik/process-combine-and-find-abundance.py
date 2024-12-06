from itertools import batched
from typing import Any, Dict, Final, List, Set, Tuple
from csv import DictReader

import concurrent.futures

from helpers.combine_fits_with_metadata import combine_fits_with_meta
from model.model_handcrafted import process_abundance_h
from constants.misc import STATISTICS_COMM_PIPE
from constants.output_dirs import OUTPUT_DIR_CLASS_FITS, OUTPUT_DIR_FIBONACCI_FITS
from constants.mongo import COLLECTION_CLASS_FITS
from helpers.download import download_file_from_file_server
from helpers.query_class import get_class_fits_at_lat_lon
from os.path import isfile


increment: Final[float] = 0.1

latitude_start: Final[float] = 30
latitude_end: Final[float] = 50

longitude_start: Final[float] = 80
longitude_end: Final[float] = 100


# latitude,longitude,al,mg,si,fe
def generate_combined_fits_for_lat_lon(
    latitude: float, longitude: float, true_mg: float, true_al: float, true_si: float, true_fe: float, redo: bool
) -> bool:
    combined_fits_path = f"{OUTPUT_DIR_FIBONACCI_FITS}/{latitude:.3f}_{longitude:.3f}.fits"
    if not redo and isfile(combined_fits_path):
        print(f"already generated: {combined_fits_path}")
        return True

    docs = get_class_fits_at_lat_lon(latitude, longitude)

    visible_element_peaks: Set[str] = set()

    for doc in docs:
        for key in doc["visible_peaks"].keys():
            visible_element_peaks.add(key)

    print(visible_element_peaks)

    file_paths: List[str] = list()
    doc_list: List[Dict[str, Any]] = list()

    for doc in docs:
        if download_file_from_file_server(doc, COLLECTION_CLASS_FITS, OUTPUT_DIR_CLASS_FITS):
            file_paths.append(f"{OUTPUT_DIR_CLASS_FITS}/{doc["path"].split("/")[-1]}")
            doc_list.append(doc)

    metadata = {"latitude": latitude, "longitude": longitude, "visible_peaks": visible_element_peaks}
    success, cam = combine_fits_with_meta(file_paths, doc_list, combined_fits_path, metadata)
    if success:
        print(f"generated: {combined_fits_path}")
        abundance_dict = process_abundance_h(combined_fits_path)
        wt_mg = abundance_dict["wt"]["Wt_Mg"]
        wt_al = abundance_dict["wt"]["Wt_Al"]
        wt_si = abundance_dict["wt"]["Wt_Si"]
        wt_ca = abundance_dict["wt"]["Wt_Ca"]
        wt_fe = abundance_dict["wt"]["Wt_Fe"]

        with open(STATISTICS_COMM_PIPE, "w") as pipe:
            pipe.write(
                (
                    f"{latitude:.3f},{longitude:.3f},"
                    f"{wt_mg:.2f},{wt_al:.2f},{wt_si:.2f},{wt_ca:.2f},{wt_fe:.2f},"
                    f"{true_mg:.2f},{true_al:.2f},{true_si:.2f},{true_fe:.2f},"
                    f"{int(cam.photon_counts.sum())},{cam.solar_zenith_angle:.2f},{cam.altitude:.2f},{cam.exposure:.2f},{cam.mid_utc},"
                    f"{cam.peak_na_c},{cam.peak_na_h:.2f},"
                    f"{cam.peak_mg_c},{cam.peak_mg_h:.2f},"
                    f"{cam.peak_al_c},{cam.peak_al_h:.2f},"
                    f"{cam.peak_si_c},{cam.peak_si_h:.2f},"
                    f"{cam.peak_ca_c},{cam.peak_ca_h:.2f},"
                    f"{cam.peak_ti_c},{cam.peak_ti_h:.2f},"
                    f"{cam.peak_fe_c},{cam.peak_fe_h:.2f}"
                    f"\n"
                )
            )

        return True
    else:
        print(f"could not generate: {combined_fits_path}")
        return False


def do_in_parallel(lat_lon_dicts: List[Dict[str, float]]):
    count = 0

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for lat_lon_dict_batch in batched(lat_lon_dicts, 32):
            future_to_doc = {
                executor.submit(
                    generate_combined_fits_for_lat_lon, lld["lat"], lld["lon"], lld["mg"], lld["al"], lld["si"], lld["fe"], True
                ): lld
                for lld in lat_lon_dict_batch
            }
            concurrent.futures.wait(future_to_doc, timeout=None, return_when=concurrent.futures.ALL_COMPLETED)

            count += 32
            print(count)


def read_lat_lon_file(csv_file_path: str) -> List[Tuple[float, float]]:
    coordinates: List[Tuple[float, float]] = list()

    with open(csv_file_path, mode="r") as file:
        reader = DictReader(file, ["latitude", "longitude"])
        for row in reader:
            # Convert latitude and longitude to float and add as a tuple
            coordinates.append((float(row["latitude"]), float(row["longitude"])))

    return coordinates


if __name__ == "__main__":
    # lat_lon_pairs: List[Tuple[float, float]] = fibonacci_sphere(400000)

    # lat_lon_pairs = lat_lon_pairs[:40000]  # get only 10% of data

    # latitude = latitude_start
    # while latitude < latitude_end:
    #     latitude += increment

    #     longitude = longitude_start
    #     while longitude < longitude_end:
    #         longitude += increment

    #         lat_lon_pairs.append((latitude, longitude))

    lat_lon_pairs = read_lat_lon_file("scripts/pointzz.csv")

    # do_in_parallel(lat_lon_pairs)

    for method in ["average", "rms", "weighted_average"]:
        generate_combined_fits_for_lat_lon(16.10, -39.09, 1, 2, 3, 4, True)
