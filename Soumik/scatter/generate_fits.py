import pandas as pd
import numpy as np
from astropy.io import fits
from astropy.table import Table


def create_fits_file(scatter_df: pd.DataFrame, output_fits_file: str):
    energy = scatter_df["keV"].values
    spectrum = scatter_df["scattered_spectrum"].values
    spectrum_scaled = spectrum * 1.1573 * 1e-8 # type: ignore
    energy_upper = energy + 0.01 # type: ignore

    primary_header = fits.Header(
        {
            "SIMPLE": True,
            "BITPIX": 8,
            "NAXIS": 0,
            "EXTEND": True,
            "MODLNAME": "scatter_model",
            "MODLUNIT": "photons/(cm^2 s)",
            "REDSHIFT": False,
            "ADDMODEL": True,
            "HDUCLASS": "OGIP",
            "HDUCLAS1": "XSPEC TABLE MODEL",
            "HDUVERS": "1.0.0",
        }
    )
    hdu0 = fits.PrimaryHDU(header=primary_header)

    params_data = np.array(
        [("addnorm", 1, 0.1, 0.01, 0.0, 0.0, 0.1, 0.2, 1, 1)],
        dtype=[
            ("NAME", "U7"),
            ("METHOD", "i2"),
            ("INITIAL", "f4"),
            ("DELTA", "f4"),
            ("MINIMUM", "f4"),
            ("BOTTOM", "f4"),
            ("TOP", "f4"),
            ("MAXIMUM", "f4"),
            ("NUMBVALS", "i2"),
            ("VALUE", "i2"),
        ],
    )
    params_table = Table(params_data)
    params_header = fits.Header(
        {
            "XTENSION": "BINTABLE",
            "EXTNAME": "PARAMETERS",
            "NINTPARM": 1,
            "NADDPARM": 0,
            "HDUCLASS": "OGIP",
            "HDUCLAS1": "XSPEC TABLE MODEL",
            "HDUCLAS2": "PARAMETERS",
            "HDUVERS": "1.0.0",
        }
    )
    hdu1 = fits.BinTableHDU(params_table, header=params_header)

    energies_data = np.column_stack((energy.astype("float32"), energy_upper.astype("float32")))
    energies_table = Table(energies_data, names=("ENERG_LO", "ENERG_HI"))
    energies_header = fits.Header(
        {
            "XTENSION": "BINTABLE",
            "EXTNAME": "ENERGIES",
            "HDUCLASS": "OGIP",
            "HDUCLAS1": "XSPEC TABLE MODEL",
            "HDUCLAS2": "ENERGIES",
            "HDUVERS": "1.0.0",
        }
    )
    hdu2 = fits.BinTableHDU(energies_table, header=energies_header)

    paramval = np.arange(0, 1.5, 0.1, dtype=np.float32)
    INTPSPEC = [spectrum_scaled + param * 1 for param in paramval]
    spectra_table = Table({"paramval": paramval, "INTPSPEC": INTPSPEC}, names=("paramval", "INTPSPEC"))
    spectra_header = fits.Header(
        {
            "XTENSION": "BINTABLE",
            "EXTNAME": "SPECTRA",
            "HDUCLASS": "OGIP",
            "HDUCLAS1": "XSPEC TABLE MODEL",
            "HDUCLAS2": "MODEL SPECTRA",
            "HDUVERS": "1.0.0",
        }
    )
    hdu3 = fits.BinTableHDU(spectra_table, header=spectra_header)

    hdul = fits.HDUList([hdu0, hdu1, hdu2, hdu3])
    hdul.writeto(output_fits_file, overwrite=True)

    print(f"FITS file written to: {output_fits_file}")


if __name__ == "__main__":
    csv_file_path = "total_scattered_spectrum.csv"
    scatter_df = pd.read_csv(csv_file_path)
    output_fits_file = "b.fits"
    create_fits_file(scatter_df, output_fits_file)
