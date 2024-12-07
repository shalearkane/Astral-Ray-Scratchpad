from typing import Any, Dict, Tuple
from helpers.xset_settings import reset_xspec, fit_and_plot, set_xset_settings
from xspec import Spectrum, Model

bin_factor = 2048
arfFile = f"model/data/{bin_factor}/class_arf_v1.arf"
respFile = f"model/data/{bin_factor}/class_rmf_v1.rmf"
background = "model/data/reference/background_allevents.fits"


def get_df_mg(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    s2 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-1.08")
    s2.ignore("1.40-**")
    m2 = Model("ga")

    m2.gaussian.LineE = 1.25  # type: ignore
    m2.gaussian.Sigma = 0.05  # type: ignore
    m2.gaussian.norm = 1  # type: ignore
    m2.gaussian.LineE.frozen = True  # type: ignore

    df, chi_2, dof = fit_and_plot()

    target_value_mg = 1.25

    row_before = df[df["energy"] <= target_value_mg].iloc[-1]
    row_after = df[df["energy"] >= target_value_mg].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]
    interpolated_value_mg = y1 + (target_value_mg - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_mg, chi_2, dof


def get_df_al(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    s2 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-1.30")
    s2.ignore("1.68-**")
    m2 = Model("ga")

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 1.48  # type: ignore
    m2.gaussian.Sigma = 0.05  # type: ignore
    m2.gaussian.norm = 1  # type: ignore
    m2.gaussian.LineE.frozen = True  # type: ignore

    df, chi_2, dof = fit_and_plot()

    target_value_al = 1.48

    row_before = df[df["energy"] <= target_value_al].iloc[-1]
    row_after = df[df["energy"] >= target_value_al].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]
    interpolated_value_al = y1 + (target_value_al - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_al, chi_2, dof


def get_df_si(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    s2 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-1.58")
    s2.ignore("1.9-**")
    m2 = Model("ga")

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 1.74  # type: ignore
    m2.gaussian.Sigma = 0.05  # type: ignore
    m2.gaussian.norm = 1  # type: ignore
    m2.gaussian.LineE.frozen = True  # type: ignore

    df, chi_2, dof = fit_and_plot()

    target_value_si = 1.74

    row_before = df[df["energy"] <= target_value_si].iloc[-1]
    row_after = df[df["energy"] >= target_value_si].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]
    interpolated_value_si = y1 + (target_value_si - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_si, chi_2, dof


def get_df_ca(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    s2 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-3.2")
    s2.ignore("4.2-**")
    m2 = Model("ga")

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 3.69  # type: ignore
    m2.gaussian.Sigma = 0.05  # type: ignore
    m2.gaussian.norm = 1  # type: ignore
    m2.gaussian.LineE.frozen = True  # type: ignore

    df, chi_2, dof = fit_and_plot()

    target_value_ca = 3.69

    row_before = df[df["energy"] <= target_value_ca].iloc[-1]
    row_after = df[df["energy"] >= target_value_ca].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]
    interpolated_value_ca = y1 + (target_value_ca - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_ca, chi_2, dof


def get_df_fe(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    s3 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s3.ignore("0.0-6.1")
    s3.ignore("6.6-**")
    m3 = Model("ga")

    # Setting values for Gaussian 1
    m3.gaussian.LineE = 6.40  # type: ignore
    m3.gaussian.Sigma = 0.05  # type: ignore
    m3.gaussian.norm = 1  # type: ignore
    m3.gaussian.LineE.frozen = True  # type: ignore

    df, chi_2, dof = fit_and_plot()

    target_value_fe = 6.40

    row_before = df[df["energy"] <= target_value_fe].iloc[-1]
    row_after = df[df["energy"] >= target_value_fe].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]
    interpolated_value_fe = y1 + (target_value_fe - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_fe, chi_2, dof


def get_df_ti(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    s3 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s3.ignore("0.0-4.2")
    s3.ignore("4.8-**")
    m3 = Model("ga")

    # Setting values for Gaussian 1
    m3.gaussian.LineE = 4.51  # type: ignore
    m3.gaussian.Sigma = 0.05  # type: ignore
    m3.gaussian.norm = 1  # type: ignore
    m3.gaussian.LineE.frozen = True  # type: ignore

    df, chi_2, dof = fit_and_plot()

    target_value_ti = 4.51

    row_before = df[df["energy"] <= target_value_ti].iloc[-1]
    row_after = df[df["energy"] >= target_value_ti].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]
    interpolated_value_ti = y1 + (target_value_ti - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_ti, chi_2, dof


def process_abundance_h(class_file: str) -> Dict[str, Dict[str, float]]:
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
    dict = process_abundance_h(
        "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/class/ch2_cla_l1_20191022T112444865_20191022T112452865.fits"
    )

    print(dict)
