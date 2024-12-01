import os
import pandas as pd
from pandas import DataFrame
from io import StringIO
import datetime
glob = None

format_string = "%d-%b-%Y %H:%M:%S.%f"

def preprocess_and_remove_duplicates(df: DataFrame, key_column: str) -> DataFrame:
    
    if key_column not in df.columns:
        raise ValueError(f"Column '{key_column}' not found in the dataframe.")

    # Sort the dataframe based on the key column
    df = df.sort_values(by=key_column).reset_index(drop=True)

    # Interpolate NaN values for numeric columns
    df = df.interpolate(method="linear", axis=0, limit_direction="both")

    # Group by the key column and calculate the mean for each group
    averaged_df = df.groupby(key_column, as_index=False).mean()

    return averaged_df

def read_and_filter_pha_file(file_path: str, start_time: datetime.datetime, end_time: datetime.datetime) -> DataFrame:
    
    with open(file_path, "r") as f_in:
        lines = f_in.readlines()
        lines = lines[5:]  # remove the first few logs
        header = lines[0].split("      ")
        header[0] = "time"  # change 'Time at center of bin'

        df = pd.read_csv(StringIO("\n".join(lines[2:])), sep="\s+", header=None)

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
    pha_files: list,
    output_file_path: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    normalize: bool = False
):
   
    # Combine data from all pha files into a single dataframe
    combined_df = pd.concat(
        [read_and_filter_pha_file(file_path, start_time, end_time) for file_path in pha_files],
        ignore_index=True
    )

    # Sum the combined dataframe values for numeric columns
    sum_df = combined_df.sum(axis=0, numeric_only=True)

    # Normalize the summed values if needed
    if normalize:
        sum_df = sum_df / len(combined_df)

    # Write the final (normalized) flux to the output file
    with open(output_file_path, "w") as f_out:
        for idx, value in zip(sum_df.index, sum_df.values):
            if "-" in idx:
                low, high = idx.split("-")
                low = float(low)
                high = float(high)
                mid = (high + low) / 2
                f_out.write(f"{mid:.2f} 0.0 {value:.4f}\n")

    # Convert the sum_df to a dataframe for easier duplicate removal
    summed_df = pd.DataFrame([sum_df])

    df_transposed = summed_df.transpose()
    # Preprocess and remove duplicates from the combined dataframe
    final_df = preprocess_and_remove_duplicates(df_transposed)

    return final_df

if __name__ == "__main__": 
    start_time = datetime.datetime(2022, 12, 22, 23, 40, 30)
    end_time = datetime.datetime(2022, 12, 22, 23, 45, 39)
    pha_files = [
        "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Pratham/GDL/ch2_xsm_20221222_v1_level2_output.txt"
    ]
    output_file_path = f"normalized_flux_{start_time.strftime('%Y%m%d%H%M')}_{end_time.strftime('%Y%m%d%H%M')}.txt"
    get_normalized_flux(pha_files, output_file_path, start_time, end_time)
