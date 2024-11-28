import os
from astropy.io import fits

def find_and_open_fits_files(folder_path):
    fits_files = []
    for root, dirs, files in os.walk(folder_path, topdown=True):
        for file in files:
            if file.endswith('.fits'):
                fits_path = os.path.join(root, file)
                fits_files.append(fits_path)

                # Open the FITS file using astropy
                with fits.open(fits_path) as hdul:
                    print(f"Opened {fits_path}")
                    # You can access data in the file here
                    # For example, to see the primary header and data:
                    print(hdul[0].header)
                    print(hdul[0].data)

    return fits_files

# Specify the path to your folder
folder_path = '/home/sm/Downloads/ch2_cla_l1_2020_11/cla/data/calibrated/2020/11/'
fits_files = find_and_open_fits_files(folder_path)

print(f"Found {len(fits_files)} FITS files.")
