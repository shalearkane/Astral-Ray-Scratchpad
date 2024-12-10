import os
from typing import Optional, Tuple
from astropy.io.fits.hdu.hdulist import HDUList
import pandas as pd
from astropy.io import fits
from helpers.utilities import to_datetime_t
from criterion.goes_solar_flare import get_flare_class
from numpy import pi
from astropy.table import Table


def photon_count_and_flare_class(fits_file: str, start_channel: int = 37, end_channel: int = 800) -> Optional[Tuple[int, str, float]]:
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
    except Exception:
        import traceback

        print(f"An error occurred while processing {fits_file}: {traceback.format_exc()}")
        return None


def photon_count_from_hdul(hdul: HDUList, start_channel: int = 37, end_channel: int = 800) -> int:
    data = hdul[1].data  # type: ignore
    channels = data["CHANNEL"]
    counts = data["COUNTS"]
    mask = (channels >= start_channel) & (channels <= end_channel)
    counts_in_range = counts[mask]
    return int(counts_in_range.sum())


def scaling_factor(hdul: HDUList) -> float:
    table = Table.read(hdul["SPECTRUM"])
    altitude = float(table.meta["SAT_ALT"])
    exposure = float(table.meta["EXPOSURE"])
    return (12.5 * 1e4 * 12.5 * (round(exposure / 8.0) + 1) * 1e8) / (exposure * 8 * pi * (altitude * 1e4) ** 2)


def photon_count(fits_file: str, start_channel: int = 37, end_channel: int = 800) -> int:
    try:
        with fits.open(fits_file) as hdul:
            return photon_count_from_hdul(hdul, start_channel, end_channel)
    except Exception:
        import traceback

        print(f"An error occurred while processing {fits_file}: {traceback.format_exc()}")
        return -1


def process_folder(folder_month: str, start_channel=15, end_channel=800) -> pd.DataFrame:
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
