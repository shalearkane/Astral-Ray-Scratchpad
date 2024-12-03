import os
from typing import Optional, Tuple
import pandas as pd
from astropy.io import fits
from datetime import datetime


def to_datetime_t(date_string: str) -> datetime:
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")


solar_flares = pd.read_csv("../data-generated/goes/solar_flares_processed.csv")
solar_flares["start_time"] = pd.to_datetime(solar_flares["start_time"])
solar_flares["end_time"] = pd.to_datetime(solar_flares["end_time"])
solar_flares.sort_values("start_time")
solar_flares["class_alphabet"] = solar_flares["class_alphabet"].astype("category")


def get_flare_class(start_time: datetime, end_time: Optional[datetime] = None) -> Tuple[str, float]:
    """Finds the key for a given time in a DataFrame with 'start_time', 'end_time', and 'key' columns.

    Args:
      df: The pandas DataFrame.
      time: The time to check.

    Returns:
      The key if found, otherwise None.
    """

    # Find the index of the first start_time greater than or equal to the given time
    matching_rows = solar_flares[(solar_flares["start_time"] <= start_time) & (solar_flares["end_time"] >= end_time)]

    if not matching_rows.empty:
        return matching_rows["class_alphabet"].iloc[0], matching_rows["class_scale"].iloc[0]
    else:
        return "None", 0


def photon_count_and_flare_class(fits_file, start_channel=15, end_channel=800) -> Optional[Tuple[int, str, float]]:
    """
    Sums the counts in the specified channel range for a given FITS file.
    """
    try:
        with fits.open(fits_file) as hdul:
            data = hdul[1].data  # type: ignore
            channels = data["CHANNEL"]
            counts = data["COUNTS"]

            metadata = hdul[1].header  # type: ignore
            start_time = to_datetime_t(metadata["STARTIME"])
            end_time = to_datetime_t(metadata["ENDTIME"])

            mask = (channels >= start_channel) & (channels <= end_channel)
            counts_in_range = counts[mask]

            flare_class, flare_scale = get_flare_class(start_time, end_time)

            return int(counts_in_range.sum()), flare_class, flare_scale
    except Exception as e:
        import traceback

        print(f"An error occurred while processing {fits_file}: {traceback.format_exc()}")
        return None


def process_folder(folder_month, start_channel=15, end_channel=800) -> pd.DataFrame:
    results = []

    for day in range(1, 32):
        print(f"processing day {day}")
        folder_day = os.path.join(folder_month, f"{day:02d}")

        for file_name in os.listdir(folder_day):

            if file_name.endswith(".fits"):
                fits_file = os.path.join(folder_day, file_name)
                count_and_class = photon_count_and_flare_class(fits_file, start_channel, end_channel)

                if count_and_class is not None:
                    count, flare_class, flare_scale = count_and_class
                    results.append({"path": file_name, "count": count, "flare_class": flare_class, "flare_scale": flare_scale})

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

    df = process_folder(folder_path)
    df.sort_values(by="count", inplace=True, ascending=False)
    df.to_csv("photon_count-1-31.csv", index=False)

    # df = pd.read_csv("photon_count.csv")
    # df.sort_values(by="count", ascending=False, inplace=True)
    # df.to_csv("photon_count_sorted.csv", index=False)

    # plot_histogram(df)
