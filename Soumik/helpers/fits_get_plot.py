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


if __name__ == "__main__":
    directory = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data-generated/fibonacci-fits"

    with fits.open("../data/class/-84.98_91.10.fits") as hdul:
        print(get_fits_plot(hdul))
