import csv
import os
import datetime
from typing import Tuple

from constants.mongo import COLLECTION_XSM_PRIMARY
from helpers.utilities import to_datetime
from constants.output_dirs import OUTPUT_DIR_SOLAR_MODEL, OUTPUT_DIR_XSM_PHA, OUTPUT_DIR_XSM_RAW_BINS
from helpers.download import download_file_from_file_server
from helpers.query_xsm import query_relevant_xsm_pha, query_xsm_pha_within_date_range
from GDL.raw_energy_bins import automate_ospex
from GDL.flux_from_raw_energy_bins import (
    filter_raw_energy_bin_file,
    output_flux_df_to_solar_model_file,
    sum_flux_across_files,
)
import pandas as pd


# Function to download XSM files
def download_xsm_files_within_date_range(start_time: datetime.datetime, end_time: datetime.datetime, output_dir: str) -> list[str]:
    docs = query_xsm_pha_within_date_range(start_time, end_time)
    os.makedirs(output_dir, exist_ok=True)

    file_paths: list[str] = list()

    for doc in docs:
        if download_file_from_file_server(doc, COLLECTION_XSM_PRIMARY, output_dir):
            file_paths.append(os.path.join(output_dir, doc["path"]))

    return file_paths


# Function to download XSM files
def download_relevant_xsm_files(start_time: datetime.datetime, end_time: datetime.datetime, output_dir: str) -> list[str]:
    docs = query_relevant_xsm_pha(start_time, end_time)
    os.makedirs(output_dir, exist_ok=True)

    file_paths: list[str] = list()

    for doc in docs:
        if download_file_from_file_server(doc, COLLECTION_XSM_PRIMARY, output_dir):
            file_paths.append(os.path.join(output_dir, doc["path"]))

    return file_paths


# Main pipeline function
def total_flux_between_dates(start_time: datetime.datetime, end_time: datetime.datetime):
    os.makedirs(OUTPUT_DIR_SOLAR_MODEL, exist_ok=True)
    pha_files = download_xsm_files_within_date_range(start_time, end_time, OUTPUT_DIR_XSM_PHA)
    raw_energy_bin_files = automate_ospex(pha_files, OUTPUT_DIR_XSM_RAW_BINS)

    sum_flux_across_files(
        raw_energy_bin_files,
        OUTPUT_DIR_SOLAR_MODEL + f"/normalized_flux_{start_time.strftime('%Y%m%d%H%M')}_{end_time.strftime('%Y%m%d%H%M')}.txt",
        start_time,
        end_time,
    )


def total_flux_for_given_date_ranges(date_ranges: list[Tuple[datetime.datetime, datetime.datetime]]) -> pd.DataFrame:
    df_list: list[pd.DataFrame] = list()
    for start_time, end_time in date_ranges:
        pha_files = download_relevant_xsm_files(start_time, end_time, OUTPUT_DIR_XSM_PHA)
        raw_energy_bin_files = automate_ospex(pha_files, OUTPUT_DIR_XSM_RAW_BINS)
        dfs = [filter_raw_energy_bin_file(file_path, start_time, end_time) for file_path in raw_energy_bin_files]

        if len(dfs) > 0:
            combined_df = pd.concat(dfs)
            df_list.append(combined_df)

        print(f"Processed flare {start_time} - {end_time}")

    return pd.concat(df_list)


def solar_model_file_with_only_flares_within_date_range(solar_flare_csv: str, start_time: datetime.datetime, end_time: datetime.datetime):
    valid_time_range = []

    with open(solar_flare_csv, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            flare_class, start_time_t, peak_time, end_time_t, noaa_active_region = row
            start_time_t = to_datetime(start_time_t)
            end_time_t = to_datetime(end_time_t)

            if start_time_t >= start_time and end_time_t <= end_time:
                valid_time_range.append((start_time_t, end_time_t))

    df = total_flux_for_given_date_ranges(valid_time_range)
    output_flux_df_to_solar_model_file(
        df, OUTPUT_DIR_SOLAR_MODEL + f"/flares_flux{start_time.strftime('%Y%m%d%H%M')}_{end_time.strftime('%Y%m%d%H%M')}.txt"
    )


if __name__ == "__main__":

    start_time = datetime.datetime(2022, 6, 27, 0, 0, 0)
    end_time = datetime.datetime(2022, 12, 27, 23, 59, 59)

    solar_model_file_with_only_flares_within_date_range("data-generated/goes/solar_flares.csv", start_time, end_time)
