from typing import Final, List

from helpers.download import download_file_from_file_server
from helpers.combine_fits import combine_fits
from helpers.query import get_class_fits_at_lat_lon

increment: Final[float] = 0.2

latitude_start: Final[float] = 35
latitude_end: Final[float] = 40

longitude_start: Final[float] = 85
longitude_end: Final[float] = 100


latitude = latitude_start
while latitude < latitude_end:
    latitude += increment

    longitude = longitude_start
    while longitude < longitude_end:
        longitude += increment

        docs = get_class_fits_at_lat_lon(latitude, longitude)
        download_folder = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/class"
        file_paths: List[str] = list()
        for doc in docs:
            if download_file_from_file_server(doc, "class", download_folder):
                file_paths.append(f"{download_folder}/{doc["path"].split("/")[-1]}")

        combined_fits_path = f"data-generated/combined-fits/{latitude:.2f}_{longitude:.2f}"
        combine_fits(file_paths, combined_fits_path)
