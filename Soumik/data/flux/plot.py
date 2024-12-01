import matplotlib

matplotlib.use("Agg")
import pandas as pd

import matplotlib.pyplot as plt


best_fit_df = pd.read_csv("some.txt", sep="\\s+", names=["Energy_keV", "error", "Spectrum_photons_per_s_per_cm2_per_keV"])
print(best_fit_df.head())
plt.figure(figsize=(10, 6))
plt.plot(best_fit_df["Energy_keV"], best_fit_df["Spectrum_photons_per_s_per_cm2_per_keV"], label="Solar Spectrum")
plt.xlabel("Energy (keV)")
plt.ylabel("Photon Flux (photons/s/cm²/keV)")
plt.yscale('log')
plt.title("Solar Spectrum Generated from GOES Temperature and Emission Measure")
plt.legend()
plt.grid(True)
plt.savefig("solar_spectrum_plot.png")
plt.show()
