from typing import Final, List, Tuple

import concurrent.futures

from constants.output_dirs import OUTPUT_DIR_CLASS_FITS
from constants.mongo import COLLECTION_CLASS_FITS
from criterion.goes_solar_flare import is_during_a_solar_flare
from helpers.download import download_file_from_file_server
from helpers.combine_fits import combine_fits
from helpers.query_class import get_class_fits_at_lat_lon
from os.path import isfile

increment: Final[float] = 0.1

latitude_start: Final[float] = 30
latitude_end: Final[float] = 50

longitude_start: Final[float] = 80
longitude_end: Final[float] = 100


def generate_combined_fits_for_lat_lon(latitude: float, longitude: float, redo: bool) -> bool:
    combined_fits_path = f"data-generated/combined-fits/{latitude:.1f}_{longitude:.1f}.fits"
    if not redo and isfile(combined_fits_path):
        print(f"already generated: {combined_fits_path}")
        return True

    docs = get_class_fits_at_lat_lon(latitude, longitude)
    filtered_docs = is_during_a_solar_flare(docs)
    file_paths: List[str] = list()
    for doc in filtered_docs:
        if download_file_from_file_server(doc, COLLECTION_CLASS_FITS, OUTPUT_DIR_CLASS_FITS):
            file_paths.append(f"{OUTPUT_DIR_CLASS_FITS}/{doc["path"].split("/")[-1]}")

    metadata = {"lat": latitude, "lon": longitude}
    if combine_fits(file_paths, combined_fits_path, metadata):
        print(f"generated: {combined_fits_path}")
        return True
    else:
        print(f"could not generate: {combined_fits_path}")
        return False


def do_in_parallel(lat_lon_pairs: List[Tuple[float, float]]):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_latlon = {executor.submit(generate_combined_fits_for_lat_lon, lat, lon, False): (lat, lon) for lat, lon in lat_lon_pairs}
        for future in concurrent.futures.as_completed(future_to_latlon):
            try:
                results.append(future.result())
            except Exception as e:
                results.append({"error": str(e)})
    return results


if __name__ == "__main__":
    lat_lon_pairs: List[Tuple[float, float]] = list()

    latitude = latitude_start
    while latitude < latitude_end:
        latitude += increment

        longitude = longitude_start
        while longitude < longitude_end:
            longitude += increment

            lat_lon_pairs.append((latitude, longitude))

    do_in_parallel(lat_lon_pairs)

    # generate_combined_fits_for_lat_lon(16.10, -39.09, True)
