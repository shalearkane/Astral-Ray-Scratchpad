import pandas as pd
from io import StringIO
import datetime

format_string = "%d-%b-%Y %H:%M:%S.%f"


def get_flux_from_energy_bins(
    input_file_path: str,
    output_file_path: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
):
    with open(input_file_path, "r") as f_in, open(output_file_path, "w") as f_out:
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

        filtered_df = df[(df["time"] >= start_time) & (df["time"] <= end_time)]
        sum_df = filtered_df.sum(axis=0, numeric_only=True)

        for idx, value in zip(sum_df.index, sum_df.values):
            low, high = idx.split("-")
            low = float(low)
            high = float(high)
            mid = (high + low) / 2
            f_out.write(f"{mid:.2f} 0.0 {value:.4f}\n")


if __name__ == "__main__":
    start_time = datetime.datetime(2022, 12, 22, 23, 40, 30)
    end_time = datetime.datetime(2022, 12, 22, 23, 45, 39)
    input_file_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Pratham/GDL/ch2_xsm_20221222_v1_level2_output.txt"
    output_file_path = "output.txt"
    get_flux_from_energy_bins(input_file_path, output_file_path, start_time, end_time)
