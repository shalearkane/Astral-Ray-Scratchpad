import os
import pandas as pd
from pandas import DataFrame
from io import StringIO
import datetime

from helpers.preprocess import preprocess_and_remove_duplicates

format_string = "%d-%b-%Y %H:%M:%S.%f"


def filter_raw_energy_bin_file(file_path: str, start_time: datetime.datetime, end_time: datetime.datetime) -> DataFrame:
    with open(file_path, "r") as f_in:
        lines = f_in.readlines()
        lines = lines[5:]  # remove the first few logs
        header = lines[0].split("      ")
        header[0] = "time"  # change 'Time at center of bin'

        df = pd.read_csv(StringIO("\n".join(lines[2:])), sep="\\s+", header=None)

        # construct the date and time into a single column
        df[0] += " " + df[1]
        df = df.drop(df.columns[[1]], axis=1)

        # set the headers
        df.columns = header

        # convert the first column into datetime objects
        df["time"] = df["time"].apply(lambda x: datetime.datetime.strptime(x, format_string))

        # Filter the dataframe based on the given time range
        filtered_df = df[(df["time"] >= start_time) & (df["time"] <= end_time)]

        return filtered_df


def get_flux_from_energy_bins(
    input_file_path: str,
    output_file_path: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
):
    filtered_df = filter_raw_energy_bin_file(input_file_path, start_time, end_time)
    sum_df = filtered_df.sum(axis=0, numeric_only=True)

    with open(output_file_path, "w") as f_out:
        for idx, value in zip(sum_df.index, sum_df.values):
            if "-" in idx:
                low, high = idx.split("-")
                low = float(low)
                high = float(high)
                mid = (high + low) / 2
                f_out.write(f"{mid:.2f} 0.0 {value:.4f}\n")


def sum_flux_across_files(
    raw_energy_bin_files: list[str],
    output_file_path: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
):

    combined_df = pd.concat([filter_raw_energy_bin_file(file_path, start_time, end_time) for file_path in raw_energy_bin_files])

    count_row = combined_df.shape[0]  # Gives number of rows
    count_col = combined_df.shape[1]  # Gives number of columns

    print(count_row)
    print(count_col)


    # Preprocess and remove duplicates from the combined dataframe
    combined_df = preprocess_and_remove_duplicates(combined_df, key_column="time")

    # Sum the combined dataframe values for numeric columns and normalize by the number of rows
    sum_df = combined_df.sum(axis=0, numeric_only=True)

    # Write the normalized flux to the output file
    with open(output_file_path, "w") as f_out:
        for idx, value in zip(sum_df.index, sum_df.values):
            if "-" in idx:
                low, high = idx.split("-")
                low = float(low)
                high = float(high)
                mid = (high + low) / 2
                f_out.write(f"{mid:.2f} 0.0 {value:.4f}\n")


if __name__ == "__main__":
    start_time = datetime.datetime(2024, 7, 22, 23, 40, 30)
    end_time = datetime.datetime(2024, 11, 22, 23, 45, 39)
    pha_files = [
        "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/raw_energy/ch2_xsm_20240827_v1_level2_output.txt",
        "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/raw_energy/ch2_xsm_20240925_v1_level2_output.txt",
    ]
    output_file_path = f"../data-generated/flux/normalized_flux_{start_time.strftime('%Y%m%d%H%M')}_{end_time.strftime('%Y%m%d%H%M')}.txt"
    sum_flux_across_files(pha_files, output_file_path, start_time, end_time)
