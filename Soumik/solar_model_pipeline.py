import os
import datetime

from helpers.download import download_file_from_file_server
from helpers.query_xsm import get_xsm_pha
from GDL.raw_energy_bins import automate_ospex
from GDL.flux_from_raw_energy_bins import get_flux_from_energy_bins, sum_flux_across_files


# Function to download XSM files
def get_xsm_files(start_time: datetime.datetime, end_time: datetime.datetime, output_dir: str) -> list[str]:
    docs = get_xsm_pha(start_time, end_time)
    os.makedirs(output_dir, exist_ok=True)

    file_paths: list[str] = list()

    for doc in docs:
        if download_file_from_file_server(doc, "primary_xsm", output_dir):
            file_paths.append(os.path.join(output_dir, doc["path"]))

    return file_paths


# Main pipeline function
def main_pipeline(start_time: datetime.datetime, end_time: datetime.datetime):
    xsm_output_dir = "data/xsm"
    raw_energy_output_dir = "data/raw_energy"
    flux_output_dir = "data/flux"

    os.makedirs(flux_output_dir, exist_ok=True)

    pha_files = get_xsm_files(start_time, end_time, xsm_output_dir)
    raw_energy_bin_files = automate_ospex(pha_files, raw_energy_output_dir)

    sum_flux_across_files(raw_energy_bin_files, flux_output_dir + "/some.txt", start_time, end_time)


if __name__ == "__main__":

    start_time = datetime.datetime(2024, 8, 27, 0, 0, 0)
    end_time = datetime.datetime(2024, 9, 27, 23, 59, 59)

    main_pipeline(start_time, end_time)
