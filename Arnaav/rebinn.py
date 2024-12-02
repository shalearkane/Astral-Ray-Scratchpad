from astropy.io import fits
import numpy as np

def bin_fits_file(original_fits, binned_fits, binning_factor=2):
    with fits.open(original_fits) as hdul:
        spectrum_hdu = hdul[1]
        data = spectrum_hdu.data
        header = spectrum_hdu.header

        channels = data['CHANNEL']
        counts = data['COUNTS']

        # Create new channel numbers ranging from 0 to (number of bins - 1)
        num_bins = len(channels) // binning_factor
        binned_channels = np.arange(num_bins, dtype=int)

        # Compute the binned counts by averaging the original counts
        binned_counts = counts[:len(counts) // binning_factor * binning_factor].reshape(-1, binning_factor).mean(axis=1)

        # Create a new binary table HDU with the binned data
        binned_data = fits.BinTableHDU.from_columns([
            fits.Column(name='CHANNEL', format='1I', array=binned_channels),
            fits.Column(name='COUNTS', format='1E', array=binned_counts)
        ])

        # Update the header
        binned_data.header.extend(header, update=True)
        binned_data.header['NAXIS2'] = len(binned_channels)
        binned_data.header['TLMAX1'] = binned_channels[-1]
        binned_data.header['DETCHANS'] = 1024 
        binned_data.header['RESPFILE'] = "class_rmf_v1.rmf"
        binned_data.header['ANCRFILE'] = "class_arf_v1.arf" # Update DETCHANS to 1024

        # Write the binned data to a new FITS file
        hdul_out = fits.HDUList([hdul[0], binned_data])
        hdul_out.writeto(binned_fits, overwrite=True)

original_fits = "ch2_cla_l1_20240808T193544720_20240808T193552720.fits"
binned_fits = "ch2_cla_l1_20240808T193544720_20240808T193552720_rebinned.fits"
bin_fits_file(original_fits, binned_fits, binning_factor=2)
