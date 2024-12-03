from astropy.io import fits

def sum_counts_in_range(fits_file, start_channel=15, end_channel=800):
   
    try:
        with fits.open(fits_file) as hdul:
            # Access the binary table HDU
            data = hdul[1].data
            
            # Extract CHANNEL and COUNTS columns
            channels = data['CHANNEL']
            counts = data['COUNTS']

            # Filter counts within the given channel range
            mask = (channels >= start_channel) & (channels <= end_channel)
            counts_in_range = counts[mask]

            # Sum and return the counts in the specified range
            return float(counts_in_range.sum())

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

#Proof of concept
fits_file = "/home/av/Documents/Code/Inter-IIT/pivot/ch2_cla_l1_20240808T193544720_20240808T193552720_rebinned.fits"
result = sum_counts_in_range(fits_file)
print(f"Sum of counts from channel 15 to 800: {result}")
