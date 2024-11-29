import numpy as np
import os
import matplotlib

import matplotlib.pyplot as plt
from astropy.io import fits


def combine_fits(folder_path: str, output_fits_path: str):
    # Folder containing the FITS files to combine

    # Get a list of all FITS files in the folder
    fits_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".fits")
    ]

    # Load and sum the counts from each FITS file
    total_counts = None
    energy_keV = None

    for file_path in fits_files:
        with fits.open(file_path) as hdul:
            data = hdul[1].data
            counts = data["COUNTS"]
            energy_channel = data["CHANNEL"]

            if total_counts is None:
                total_counts = np.zeros_like(counts)
                energy_keV = (
                    energy_channel * 0.0135
                )  # Convert channels to keV (assuming same across all files)

            total_counts += counts

    # Save the combined data to a new FITS file
    hdu = fits.BinTableHDU.from_columns(
        [
            fits.Column(name="CHANNEL", format="1I", array=energy_channel),
            fits.Column(name="COUNTS", format="1D", array=total_counts),
        ]
    )
    hdu.header["EXTNAME"] = "SPECTRUM"
    hdu.header["HDUCLASS"] = "OGIP"
    hdu.header["HDUCLAS1"] = "SPECTRUM"
    hdu.header["HDUVERS1"] = "1.1.0"
    hdu.header["HDUVERS"] = "1.1.0"
    hdu.header["HDUCLAS2"] = "TOTAL"
    hdu.header["HDUCLAS3"] = "COUNT"
    hdu.header["TLMIN1"] = 0
    hdu.header["TLMAX1"] = 2047
    hdu.header["TELESCOP"] = "CHANDRAYAAN-2"
    hdu.header["INSTRUME"] = "CLASS"
    hdu.header["FILTER"] = "none"
    hdu.header["EXPOSURE"] = 8.0
    hdu.header["AREASCAL"] = 1.0
    hdu.header["BACKFILE"] = "NONE"
    hdu.header["BACKSCAL"] = 1.0
    hdu.header["CORRFILE"] = "NONE"
    hdu.header["CORRSCAL"] = 1.0
    hdu.header["RESPFILE"] = "class_rmf_v1.rmf"
    hdu.header["ANCRFILE"] = "class_arf_v1.arf"
    hdu.header["PHAVERSN"] = "1992a"
    hdu.header["DETCHANS"] = 2048
    hdu.header["CHANTYPE"] = "PHA"
    hdu.header["POISSERR"] = "True"
    hdu.header["STAT_ERR"] = 0
    hdu.header["SYS_ERR"] = 0
    hdu.header["GROUPING"] = 0
    hdu.header["QUALITY"] = 0
    hdu.header["EQUINOX"] = 2000.0
    hdu.header["DATE"] = "Sun Dec  6 14:23:21 2020"
    hdu.header["PROGRAM"] = "CLASS_add_scds.pro"
    hdu.header["IPFILE"] = "CLA01D18CHO0195703016020032073056411_08.pld"
    hdu.header["DATASET"] = 249
    hdu.header["STARTIME"] = "20200201T000000114"
    hdu.header["ENDTIME"] = "20200201T000008114"
    hdu.header["TEMP"] = -43.7
    hdu.header["GAIN"] = 13.5
    hdu.header["SCD_USED"] = "0,1,2,3,4,5,6,7,8,9,10,11"
    hdu.header["MID_UTC"] = "2020-02-01T00:00:04.114"
    hdu.header["SAT_ALT"] = 79.1612
    hdu.header["SAT_LAT"] = -18.0006
    hdu.header["SAT_LON"] = 61.818
    hdu.header["LST_HR"] = 9
    hdu.header["LST_MIN"] = 36
    hdu.header["LST_SEC"] = 48
    hdu.header["BORE_LAT"] = -18.0026
    hdu.header["BORE_LON"] = 61.8179
    hdu.header["V0_LAT"] = -17.4623
    hdu.header["V1_LAT"] = -18.5262
    hdu.header["V2_LAT"] = -18.5379
    hdu.header["V3_LAT"] = -17.4739
    hdu.header["V0_LON"] = 61.486
    hdu.header["V1_LON"] = 61.4647
    hdu.header["V2_LON"] = 62.1519
    hdu.header["V3_LON"] = 62.1688
    hdu.header["SOLARANG"] = 39.1038
    hdu.header["PHASEANG"] = 39.1038
    hdu.header["EMISNANG"] = 1.3486838e-09

    hdu.writeto(output_fits_path, overwrite=True)


if __name__ == "__main__":
    folder_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/class"
    output_fits_path = "combined.fits"
    combine_fits(folder_path, output_fits_path)
    exit(0)

    # Load the combined FITS file and plot the data
    with fits.open(output_fits_path) as hdul:
        hdul.info()  # Print information about the FITS file
        data = hdul[1].data  # Access the data from the second HDU (index 1)
        energy_keV = data["CHANNEL"] * 0.0135  # Convert channels to keV
        counts = data["COUNTS"]

        # Ensure data can be plotted
        energy_keV = np.array(energy_keV, dtype=float)
        counts = np.array(counts, dtype=float)

        # Filter energy values up to 7 keV
        mask = (energy_keV >= 1.0) & (energy_keV <= 2.0)
        energy_keV = energy_keV[mask]
        counts = counts[mask]

        # Plot the spectrum
        matplotlib.use("Agg")

        plt.figure(figsize=(10, 6))
        plt.plot(
            energy_keV, counts, label="Combined Spectrum", linestyle="-", color="blue"
        )
        plt.xlabel("Energy (keV)")
        plt.ylabel("Counts")
        plt.legend()
        plt.title("Combined Spectrum from FITS Files")
        plt.grid(True)
        plt.savefig("combined_spectrum_plot.png")
