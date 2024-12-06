from typing import Dict
from astropy.io import fits
from astropy.io.fits import HDUList
import numpy as np
from scipy.signal import find_peaks, savgol_filter


def generate_visible_peaks(hdul: HDUList) -> Dict[str, float]:
    tolerance = 0.05
    element_kalpha_lines = {"Na": 1.04, "Mg": 1.25, "Al": 1.48, "Si": 1.74, "Ca": 3.69, "Ti": 4.51, "Fe": 6.40}

    try:
        data = hdul[1].data  # type: ignore

        channels = data["CHANNEL"][60:485]
        smooth_counts = data["COUNTS"][60:485]

        min_value = np.min(smooth_counts)
        max_value = np.max(smooth_counts)
        normalized_counts = (100 * (smooth_counts - min_value)) / (max_value - min_value)
        smooth_counts = savgol_filter(normalized_counts, window_length=20, polyorder=4)

        gain = 13.61 / 1000.0
        energy = channels * gain

        peaks, peak_properties = find_peaks(smooth_counts, distance=10, height=4)
        peak_energies: np.ndarray = energy[peaks]

        results: Dict[str, float] = {}
        for idx, peak in enumerate(peak_energies):
            for element, kalpha_line in element_kalpha_lines.items():
                if abs(peak - kalpha_line) <= tolerance:
                    results[element] = max(peak_properties["peak_heights"][idx] + (min_value * gain), results.get(element, 0))

        return results

    except Exception:
        import traceback

        print(f"An error occurred: {traceback.format_exc()}")
        return {}


if __name__ == "__main__":
    directory = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data-generated/fibonacci-fits"

    with fits.open("/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/x-class.fits") as hdul:
        generate_visible_peaks(hdul)
