from typing import Final, List, Tuple

import concurrent.futures

from helpers.download import download_file_from_file_server
from helpers.combine_fits import combine_fits
from helpers.query import get_class_fits_at_lat_lon

increment: Final[float] = 0.1

latitude_start: Final[float] = 30
latitude_end: Final[float] = 50

longitude_start: Final[float] = 80
longitude_end: Final[float] = 100

download_folder = "data/class"


def generate_combined_fits_for_lat_lon(latitude: float, longitude: float):
    docs = get_class_fits_at_lat_lon(latitude, longitude)
    file_paths: List[str] = list()
    for doc in docs:
        if download_file_from_file_server(doc, "primary", download_folder):
            file_paths.append(f"{download_folder}/{doc["path"].split("/")[-1]}")

    combined_fits_path = f"data-generated/combined-fits/{latitude:.1f}_{longitude:.1f}.fits"
    metadata = {"lat": latitude, "lon": longitude}
    if combine_fits(file_paths, combined_fits_path, metadata):
        print(f"generated: {combined_fits_path}")
    else:
        print(f"could not generate: {combined_fits_path}")


def do_in_parallel(lat_lon_pairs: List[Tuple[float, float]]):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_latlon = {executor.submit(generate_combined_fits_for_lat_lon, lat, lon): (lat, lon) for lat, lon in lat_lon_pairs}
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
