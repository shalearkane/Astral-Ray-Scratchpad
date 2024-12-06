import matplotlib

from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks, savgol_filter
import os

matplotlib.use("Agg")


def process_fits(file_path, output_image="filtered_plot.png"):
    tolerance = 0.05
    targets = {"Na": 1.04, "Mg": 1.25, "Al": 1.48, "Si": 1.74, "Ca": 3.69, "Ti": 4.51, "Fe": 6.40}

    output_image = os.path.join(f"output_pics/{file_path.split("/")[-1][:-5]}.png")

    try:
        with fits.open(file_path) as hdul:
            data = hdul[1].data

            channels = data["CHANNEL"][70:300]
            counts = data["COUNTS"][70:300]

            min_value = np.min(counts)
            max_value = np.max(counts)
            normalized_counts = 100 * (counts - min_value) / (max_value - min_value)
            counts = savgol_filter(normalized_counts, window_length=20, polyorder=4)

            gain = 13.61 / 1000.0
            energy = channels * gain

            peaks, _ = find_peaks(counts, distance=10, height=5)
            peak_energies = energy[peaks]

            results = {element: False for element in targets}
            for peak in peak_energies:
                for element, target in targets.items():
                    if abs(peak - target) <= tolerance:
                        results[element] = True

            print(results)
            plt.plot(channels, counts, color="red", label="Peaks", zorder=5)

            for peak in peaks:
                plt.text(channels[peak], counts[peak] + 1, f"{energy[peak]:.2f} keV", fontsize=10, ha="center")

            plt.title("Filtered Spectrum from 1-2 keV with Peaks", fontsize=16)
            plt.xlabel("Channels", fontsize=14)
            plt.ylabel("Counts", fontsize=14)
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.legend(fontsize=12)
            plt.tight_layout()
            plt.savefig(output_image)

            plt.clf()

            return tuple(results[element] for element in ["Mg", "Al", "Si", "Ca"])

    except Exception as e:
        print(f"An error occurred: {e}")
        return (False, False, False, False)


if __name__ == "__main__":
    file_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/x-class.fits"
    result = process_fits(file_path)
    print(result)

    # directory = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data-generated/fibonacci-fits"
