import os
import datetime
from typing import Tuple

from constants.output_dirs import OUTPUT_DIR_SOLAR_MODEL, OUTPUT_DIR_XSM_PHA, OUTPUT_DIR_XSM_RAW_BINS
from helpers.download import download_file_from_file_server
from helpers.query_xsm import get_xsm_pha
from GDL.raw_energy_bins import automate_ospex
from GDL.flux_from_raw_energy_bins import filter_raw_energy_bin_file, get_flux_from_energy_bins, sum_flux_across_files
import pandas as pd


# Function to download XSM files
def get_xsm_files(start_time: datetime.datetime, end_time: datetime.datetime, output_dir: str) -> list[str]:
    docs = get_xsm_pha(start_time, end_time)
    os.makedirs(output_dir, exist_ok=True)

    file_paths: list[str] = list()

    for doc in docs:
        if download_file_from_file_server(doc, "xsm_primary", output_dir):
            file_paths.append(os.path.join(output_dir, doc["path"]))

    return file_paths


# Main pipeline function
def total_flux_between_dates(start_time: datetime.datetime, end_time: datetime.datetime):
    os.makedirs(OUTPUT_DIR_SOLAR_MODEL, exist_ok=True)
    pha_files = get_xsm_files(start_time, end_time, OUTPUT_DIR_XSM_PHA)
    raw_energy_bin_files = automate_ospex(pha_files, OUTPUT_DIR_XSM_RAW_BINS)

    sum_flux_across_files(
        raw_energy_bin_files,
        OUTPUT_DIR_SOLAR_MODEL + f"/normalized_flux_{start_time.strftime('%Y%m%d%H%M')}_{end_time.strftime('%Y%m%d%H%M')}.txt",
        start_time,
        end_time,
    )


def total_flux_for_given_date_ranges(date_ranges: list[Tuple[datetime.datetime, datetime.datetime]]):
    df_list: list[pd.DataFrame] = list()
    for start_time, end_time in date_ranges:
        pha_files = get_xsm_files(start_time, end_time, OUTPUT_DIR_XSM_PHA)
        raw_energy_bin_files = automate_ospex(pha_files, OUTPUT_DIR_XSM_RAW_BINS)
        combined_df = pd.concat([filter_raw_energy_bin_file(file_path, start_time, end_time) for file_path in raw_energy_bin_files])
        df_list.append(combined_df)

    df = pd.concat(df_list)

    df.to_csv("solar_flare_fluxes.csv")


if __name__ == "__main__":

    start_time = datetime.datetime(2022, 7, 27, 0, 0, 0)
    end_time = datetime.datetime(2022, 12, 27, 23, 59, 59)

    total_flux_between_dates(start_time, end_time)
