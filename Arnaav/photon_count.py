import os
from typing import Optional
import pandas as pd
from astropy.io import fits
import numpy as np

def find_key(df, time):
  """Finds the key for a given time in a DataFrame with 'start_time', 'end_time', and 'key' columns.

  Args:
    df: The pandas DataFrame.
    time: The time to check.

  Returns:
    The key if found, otherwise None.
  """

  # Sort the DataFrame by start_time
  df = df.sort_values('start_time')

  # Convert time to datetime if necessary
  time = pd.to_datetime(time)

  # Find the index of the first start_time greater than or equal to the given time
  index = np.searchsorted(df['start_time'].values, time)

  # If the index is 0 or the time is not within the range of any interval, return None
  if index == 0 or time < df['start_time'].iloc[index - 1]:
    return None

  # Otherwise, return the key at the previous index
  return df['key'].iloc[index - 1]


def sum_counts_in_range(fits_file, start_channel=15, end_channel=800) -> Optional[int]:
    """
    Sums the counts in the specified channel range for a given FITS file.
    """
    try:
        with fits.open(fits_file) as hdul:
            data = hdul[1].data  # type: ignore
            channels = data["CHANNEL"]
            counts = data["COUNTS"]

            mask = (channels >= start_channel) & (channels <= end_channel)
            counts_in_range = counts[mask]

            return int(counts_in_range.sum())
    except Exception as e:
        print(f"An error occurred while processing {fits_file}: {e}")
        return None


def process_folder(folder_month, start_channel=15, end_channel=800) -> pd.DataFrame:
    results = []

    for day in range(1, 32):
        print(f"processing day {day}")
        folder_day = os.path.join(folder_month, f"{day:02d}")

        for file_name in os.listdir(folder_day):

            if file_name.endswith(".fits"):
                fits_file = os.path.join(folder_day, file_name)
                sum_counts = sum_counts_in_range(fits_file, start_channel, end_channel)

                if sum_counts is not None:
                    results.append({"path": file_name, "count": sum_counts})

    df = pd.DataFrame(results)

    return df


def plot_histogram(df: pd.DataFrame):
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.use("Agg")
    photon_counts = df["count"]

    # Plot the histogram
    plt.figure(figsize=(18, 6))
    plt.hist(photon_counts, bins=1000, range=(200, 20000), color="skyblue", edgecolor="black")
    plt.xlabel("Photon Count")
    plt.ylabel("Frequency")
    plt.title("Histogram of Photon Counts")
    plt.grid(axis="y", alpha=0.75)
    plt.xscale("log")
    plt.xticks(
        [200, 400, 800, 1000, 2000, 4000, 8000, 10000, 16000, 20000],
        ["200", "400", "800" "1000", "2000", "4000", "8000", "10000", "16000", "20000", "24000"],
    )
    plt.savefig("photon-count-histogram.png")


if __name__ == "__main__":
    folder_path = "/home/sm/Downloads/ch2_cla_l1_2024_07/cla/data/calibrated/2024/07"

    # df = process_folder(folder_path)
    # df.sort_values(by="count")
    # df.to_csv("photon_count.csv", index=False)

    df = pd.read_csv("photon_count.csv")
    df.sort_values(by="count", ascending=False, inplace=True)
    df.to_csv("photon_count_sorted.csv", index=False)

    plot_histogram(df)
