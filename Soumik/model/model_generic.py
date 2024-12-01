from xspec import *
from astropy.io import fits
from functions.xrf_localmodel import LocalModel_Parameters, create_xrf_localmodel


def process_abundance(class_l1: str, background: str, solar: str, scatter_atable: str, bin_size: int):
    ignore_erange = ["0.9", "4.2"]
    ignore_string = "0.0-" + ignore_erange[0] + " " + ignore_erange[1] + "-**"

    # Getting the information for making the static parameter file
    hdu_data = fits.open(class_l1)
    hdu_header = hdu_data[1].header  # type: ignore
    hdu_data.close()

    localmodel_params = LocalModel_Parameters(
        solar, hdu_header["SOLARANG"], hdu_header["EMISNANG"], hdu_header["SAT_ALT"], hdu_header["EXPOSURE"]
    )

    # PyXspec Initialisation
    AllData.clear()
    AllModels.clear()
    Xset.parallel.show()
    N = 8
    Xset.parallel.error = N
    Xset.parallel.goodness = N
    Xset.parallel.leven = N
    Xset.parallel.steppar = N
    Xset.parallel.walkers = N
    Xset.allowPrompting = False

    spec_data = Spectrum(class_l1, backFile=background, respFile=f"data/{str(bin_size)}/class_rmf_v1.rmf", arfFile=f"data/{str(bin_size)}/class_arf_v1.arf")
    spec_data.ignore(ignore_string)

    # Defining model and fitting
    spec_data.response.gain.slope = "1.0043000"
    spec_data.response.gain.offset = "0.0316000"
    spec_data.response.gain.slope.frozen = True  # type: ignore
    spec_data.response.gain.offset.frozen = True  # type: ignore

    create_xrf_localmodel(localmodel_params)

    full_model = "atable{" + scatter_atable + "} + xrf_localmodel"
    mo = Model(full_model)
    mo(10).values = "45.0"
    mo(10).frozen = True
    mo(1).frozen = True
    mo(6).link = "100 - (3+4+5+7+8+9+10)"

    Fit.nIterations = 100
    Fit.perform()


if __name__ == "__main__":
    class_l1 = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data-generated/combined-fits/35.20_85.20.fits"
    background = "data/reference/background_allevents.fits"
    solar = "data/reference/modelop_20210827T210316000_20210827T210332000.txt"
    scatter_atable = "data/reference/tbmodel_20210827T210316000_20210827T210332000.fits"

    process_abundance(class_l1, background, solar, scatter_atable, bin_size=2048)
