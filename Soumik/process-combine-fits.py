from itertools import batched
from typing import Final, List, Set, Tuple
from csv import DictReader

import concurrent.futures

from constants.output_dirs import OUTPUT_DIR_CLASS_FITS, OUTPUT_DIR_TRUTH_FITS
from constants.mongo import COLLECTION_CLASS_FITS
from helpers.download import download_file_from_file_server
from helpers.combine_fits_mod import combine_fits
from helpers.query_class import get_class_fits_at_lat_lon
from os.path import isfile

increment: Final[float] = 0.1

latitude_start: Final[float] = 30
latitude_end: Final[float] = 50

longitude_start: Final[float] = 80
longitude_end: Final[float] = 100


def generate_combined_fits_for_lat_lon(latitude: float, longitude: float, redo: bool, method: str = "weighted_average") -> bool:
    combined_fits_path = f"{OUTPUT_DIR_TRUTH_FITS}/{latitude:.3f}_{longitude:.3f}_{method}.fits"
    if not redo and isfile(combined_fits_path):
        print(f"already generated: {combined_fits_path}")
        return True

    docs = get_class_fits_at_lat_lon(latitude, longitude)

    visible_element_peaks: Set[str] = set()

    for doc in docs:
        for key in doc["visible_peaks"].keys():
            visible_element_peaks.add(key)

    file_paths: List[str] = list()

    for doc in docs:
        if download_file_from_file_server(doc, COLLECTION_CLASS_FITS, OUTPUT_DIR_CLASS_FITS):
            file_paths.append(f"{OUTPUT_DIR_CLASS_FITS}/{doc["path"].split("/")[-1]}")

    metadata = {"latitude": latitude, "longitude": longitude, "visible_peaks": visible_element_peaks}
    if combine_fits(file_paths, combined_fits_path, metadata, method):
        print(f"generated: {combined_fits_path}")
        return True
    else:
        print(f"could not generate: {combined_fits_path}")
        return False


def do_in_parallel(lat_lon_pairs: List[Tuple[float, float]]):
    count = 0

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for lat_lon_pair_batch in batched(lat_lon_pairs, 32):
            future_to_doc = {
                executor.submit(generate_combined_fits_for_lat_lon, lat, lon, True): (lat, lon) for (lat, lon) in lat_lon_pair_batch
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

    lat_lon_pairs = read_lat_lon_file("data-generated/script_inputs/points.csv")

    do_in_parallel(lat_lon_pairs)

    # for method in ["average", "rms", "weighted_average"]:
    #     generate_combined_fits_for_lat_lon(16.10, -39.09, True, method)
