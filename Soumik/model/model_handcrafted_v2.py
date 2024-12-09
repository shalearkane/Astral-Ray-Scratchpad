from typing import Any, Dict, Tuple
from helpers.xset_settings import reset_xspec, fit, set_xset_settings
from xspec import Spectrum, Model

bin_factor = 2048
arfFile = f"model/data/{bin_factor}/class_arf_v1.arf"
respFile = f"model/data/{bin_factor}/class_rmf_v1.rmf"
background = "model/data/reference/background_allevents.fits"


def get_df_mg(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    spectrum = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    spectrum.ignore("0.0-1.08")
    spectrum.ignore("1.40-**")
    model = Model("ga")

    model.gaussian.LineE = 1.2536  # type: ignore
    model.gaussian.Sigma = 0.05  # type: ignore
    model.gaussian.norm = 1  # type: ignore
    model.gaussian.LineE.frozen = True  # type: ignore

    chi_2, dof = fit()
    norm = model.gaussian.norm.values[0]  # type: ignore

    return norm, chi_2, dof


def get_df_al(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    spectrum = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    spectrum.ignore("0.0-1.30")
    spectrum.ignore("1.64-**")
    model = Model("ga")

    # Setting values for Gaussian 1
    model.gaussian.LineE = 1.4867  # type: ignore
    model.gaussian.Sigma = 0.05  # type: ignore
    model.gaussian.norm = 1  # type: ignore
    model.gaussian.LineE.frozen = True  # type: ignore

    chi_2, dof = fit()
    norm = model.gaussian.norm.values[0]  # type: ignore

    return norm, chi_2, dof


def get_df_si(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    spectrum = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    spectrum.ignore("0.0-1.58")
    spectrum.ignore("1.9-**")
    model = Model("ga")

    # Setting values for Gaussian 1
    model.gaussian.LineE = 1.73998  # type: ignore
    model.gaussian.Sigma = 0.05  # type: ignore
    model.gaussian.norm = 1  # type: ignore
    model.gaussian.LineE.frozen = True  # type: ignore

    chi_2, dof = fit()
    norm = model.gaussian.norm.values[0]  # type: ignore

    return norm, chi_2, dof


def get_df_ca(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    spectrum = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    spectrum.ignore("0.0-3.2")
    spectrum.ignore("4.2-**")
    model = Model("ga")

    # Setting values for Gaussian 1
    model.gaussian.LineE = 3.69168  # type: ignore
    model.gaussian.Sigma = 0.05  # type: ignore
    model.gaussian.norm = 1  # type: ignore
    model.gaussian.LineE.frozen = True  # type: ignore

    chi_2, dof = fit()
    norm = model.gaussian.norm.values[0]  # type: ignore

    return norm, chi_2, dof


def get_df_fe(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    spectrum = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    spectrum.ignore("0.0-6.1")
    spectrum.ignore("6.6-**")
    model = Model("ga")

    # Setting values for Gaussian 1
    model.gaussian.LineE = 6.40384  # type: ignore
    model.gaussian.Sigma = 0.05  # type: ignore
    model.gaussian.norm = 1  # type: ignore
    model.gaussian.LineE.frozen = True  # type: ignore

    chi_2, dof = fit()
    norm = model.gaussian.norm.values[0]  # type: ignore

    return norm, chi_2, dof


def get_df_ti(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    spectrum = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    spectrum.ignore("0.0-4.2")
    spectrum.ignore("4.8-**")
    model = Model("ga")

    # Setting values for Gaussian 1
    model.gaussian.LineE = 4.51084  # type: ignore
    model.gaussian.Sigma = 0.05  # type: ignore
    model.gaussian.norm = 1  # type: ignore
    model.gaussian.LineE.frozen = True  # type: ignore

    chi_2, dof = fit()
    norm = model.gaussian.norm.values[0]  # type: ignore

    return norm, chi_2, dof


def process_abundance_h_v2(class_file: str) -> Dict[str, Dict[str, float]]:
    set_xset_settings()

    mg, mg_chi_2, mg_dof = get_df_mg(class_file)
    al, al_chi_2, al_dof = get_df_al(class_file)
    si, si_chi_2, si_dof = get_df_si(class_file)
    ca, ca_chi_2, ca_dof = get_df_ca(class_file)
    ti, ti_chi_2, ti_dof = get_df_ti(class_file)
    fe, fe_chi_2, fe_dof = get_df_fe(class_file)

    dict = {
        "filename": {"class_file": class_file},
        "wt": {"mg": mg, "al": al, "si": si, "ca": ca, "ti": ti, "fe": fe},
        "chi_2": {"mg": mg_chi_2, "al": al_chi_2, "si": si_chi_2, "ca": ca_chi_2, "ti": ti_chi_2, "fe": fe_chi_2},
        "dof": {"mg": mg_dof, "al": al_dof, "si": si_dof, "ca": ca_dof, "ti": ti_dof, "fe": fe_dof},
    }

    return dict


if __name__ == "__main__":
    dict = process_abundance_h_v2("/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/-0.00_2.41.fits")

    print(dict)
