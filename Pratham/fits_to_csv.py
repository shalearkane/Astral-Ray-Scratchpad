from astropy.io import fits
from astropy.table import Table

# set memmap=True for large files
hdu_list =  fits.open("/home/pg/Downloads/ch2_xsm_20241016_v1/xsm/data/2024/10/16/raw/ch2_xsm_20241016_v1_level1.fits", memmap=True)
print(hdu_list.info())
    # select the HDU you want
hdu = hdu_list[1].data
    # read into an astropy Table object
table = Table(hdu)

    # write to a CSV file
table.write('/home/pg/ISRO_Inter_IIT/file2.csv', delimiter=',', format='ascii.ecsv',overwrite=True)