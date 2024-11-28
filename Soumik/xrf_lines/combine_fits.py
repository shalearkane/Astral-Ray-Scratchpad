import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from astropy.io import fits

# Folder containing the FITS files to combine
folder_path = '04'

# Get a list of all FITS files in the folder
fits_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.fits')]

# Load and sum the counts from each FITS file
total_counts = None
energy_keV = None

for file_path in fits_files:
    with fits.open(file_path) as hdul:
        data = hdul[1].data
        counts = data['COUNTS']
        energy_channel = data['CHANNEL']

        if total_counts is None:
            total_counts = np.zeros_like(counts)
            energy_keV = energy_channel * 0.0135  # Convert channels to keV (assuming same across all files)

        total_counts += counts

# Save the combined data to a new FITS file
hdu = fits.BinTableHDU.from_columns([
    fits.Column(name='CHANNEL', format='1I', array=energy_channel),
    fits.Column(name='COUNTS', format='1D', array=total_counts)
])
hdu.writeto('combined_96s.fits', overwrite=True)

# Load the combined FITS file and plot the data
with fits.open('combined_96s.fits') as hdul:
    hdul.info()  # Print information about the FITS file
    data = hdul[1].data  # Access the data from the second HDU (index 1)
    energy_keV = data['CHANNEL'] * 0.0135  # Convert channels to keV
    counts = data['COUNTS']


      # Ensure data can be plotted
    energy_keV = np.array(energy_keV, dtype=float)
    counts = np.array(counts, dtype=float)

    # Filter energy values up to 7 keV
    mask = (energy_keV >= 1.0) & (energy_keV <= 2.0)
    energy_keV = energy_keV[mask]
    counts = counts[mask]

    # Plot the spectrum
    plt.figure(figsize=(10, 6))
    plt.plot(energy_keV, counts, label='Combined Spectrum', linestyle='-', color='blue')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Counts')
    plt.legend()
    plt.title('Combined Spectrum from FITS Files')
    plt.grid(True)
    plt.savefig('combined_spectrum_plot.png')