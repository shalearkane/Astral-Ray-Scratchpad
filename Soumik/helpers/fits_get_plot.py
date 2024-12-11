from typing import Dict, List
from astropy.io import fits
from astropy.io.fits import HDUList


def get_fits_plot(hdul: HDUList) -> List[Dict[str, float]]:
    try:
        data = hdul[1].data  # type: ignore
        counts = data["COUNTS"]
        plot_info = list()

        for idx, count in enumerate(counts):
            plot_info.append({"channelNumber": idx, "count": float(count)})

        return plot_info
    except Exception:
        import traceback

        print(f"An error occurred: {traceback.format_exc()}")
        return []


def get_fits_plot_from_fits_file(fits_file: str) -> List[Dict[str, float]]:
    with fits.open(fits_file, "readonly") as hdul:
        return get_fits_plot(hdul)


def get_fits_plot_array(fits_file: str) -> List[float]:
    with fits.open(fits_file, "readonly") as hdul:
        data = hdul[1].data  # type: ignore
        counts = data["COUNTS"][60:800]

        return list(counts)


if __name__ == "__main__":
    directory = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data-generated/fibonacci-fits"

    with fits.open("../data/class/-84.98_91.10.fits") as hdul:
        print(get_fits_plot(hdul))
