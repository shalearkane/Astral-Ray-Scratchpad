from criterion.photon_count import photon_count_from_hdul

from astropy.io import fits

with fits.open("x-class.fits") as f:
    print(photon_count_from_hdul(f))
