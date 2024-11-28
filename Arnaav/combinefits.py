import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from astropy.io import fits

# Folder containing the FITS files to combine
folder_path = 'class'

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

hdu.header['EXTNAME']  = 'SPECTRUM'
hdu.header['HDUCLASS']  = 'OGIP'
hdu.header['HDUCLAS1']  = 'SPECTRUM'
hdu.header['HDUVERS1']  = '1.1.0'
hdu.header['HDUVERS']  = '1.1.0'
hdu.header['HDUCLAS2']  = 'TOTAL'
hdu.header['HDUCLAS3']  = 'COUNT'
hdu.header['TLMIN1']  = 0
hdu.header['TLMAX1']  = 2047
hdu.header['TELESCOP']  = 'CHANDRAYAAN-2'
hdu.header['INSTRUME']  = 'CLASS'
hdu.header['FILTER']  = 'none'
hdu.header['EXPOSURE']  = '16'
hdu.header['AREASCAL']  = '1.0'
hdu.header['BACKFILE']  = 'NONE'
hdu.header['BACKSCAL']  = '1.0'
hdu.header['CORRFILE']  = 'NONE'
hdu.header['CORRSCAL']  = '1.0'
hdu.header['RESPFILE']  = 'class_rmf_v1.rmf'
hdu.header['ANCRFILE']  = 'class_arf_v1.arf'
hdu.header['PHAVERSN']  = '1992a'
hdu.header['DETCHANS']  = '2048'
hdu.header['CHANTYPE']  = 'PHA'
hdu.header['POISSERR']  = 'True'
hdu.header['STAT_ERR']  = '0'
hdu.header['SYS_ERR']  = '0'
hdu.header['GROUPING']  = '0'
hdu.header['QUALITY']  = '0'
hdu.header['EQUINOX']  = '2000.0'
hdu.header['DATE']  = 'Thu Mar 17 17:41:51 2022'
hdu.header['PROGRAM']  = 'generate_spectrum_from_spectrogram.pro'
hdu.header['STARTIME']  = '2021-08-27T21:03:16.000'
hdu.header['ENDTIME']  = '2021-08-27T21:03:32.000'
hdu.header['GAIN']  = '27.0'
hdu.header['SCD_USED']  = '0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15'
hdu.header['MID_UTC']  = '2021-08-27T21:03:24.000'
hdu.header['SAT_ALT']  = '113.779'
hdu.header['SAT_LAT']  = '-13.7739'
hdu.header['SAT_LON']  = '-123.762'
hdu.header['LST_HR']  = '7'
hdu.header['LST_MIN']  = '46'
hdu.header['LST_SEC']  = '48'
hdu.header['BORE_LAT']  = '-13.7739'
hdu.header['BORE_LON']  = '-123.762'
hdu.header['V0_LAT']  = '-12.9754'
hdu.header['V1_LAT']  = '-14.7087'
hdu.header['V2_LAT']  = '-14.5669'
hdu.header['V3_LAT']  = '-12.8399'
hdu.header['V0_LON']  = '-124.311'
hdu.header['V1_LON']  = '-124.163'
hdu.header['V2_LON']  = '-123.206'
hdu.header['V3_LON']  = '-123.359'
hdu.header['SOLARANG']  = '64.55'
hdu.header['PHASEANG']  = '64.55'
hdu.header['EMISNANG']  = '3.83034e-09'
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
