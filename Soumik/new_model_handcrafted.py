from typing import Any, Dict, Tuple
from helpers.xset_settings import reset_xspec, fit_and_plot, set_xset_settings
from xspec import Spectrum, Model
import pandas as pd

bin_factor = 2048
arfFile = f"model/data/{bin_factor}/class_arf_v1.arf"
respFile = f"model/data/{bin_factor}/class_rmf_v1.rmf"
background = "model/data/reference/background_allevents.fits"


def get_df_mg(class_file: str) -> pd.DataFrame:
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

    # row_before = df[df["energy"] <= target_value_mg].iloc[-1]
    # row_after = df[df["energy"] >= target_value_mg].iloc[0]
    # x1, x2 = row_before["energy"], row_after["energy"]
    # y1, y2 = row_before["counts"], row_after["counts"]
    # interpolated_value_mg = y1 + (target_value_mg - x1) * (y2 - y1) / (x2 - x1)

    return df


def get_df_al(class_file: str) -> pd.DataFrame:
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

    # row_before = df[df["energy"] <= target_value_al].iloc[-1]
    # row_after = df[df["energy"] >= target_value_al].iloc[0]
    # x1, x2 = row_before["energy"], row_after["energy"]
    # y1, y2 = row_before["counts"], row_after["counts"]
    # interpolated_value_al = y1 + (target_value_al - x1) * (y2 - y1) / (x2 - x1)

    return df


def get_df_si(class_file: str) -> pd.DataFrame:
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

    # row_before = df[df["energy"] <= target_value_si].iloc[-1]
    # row_after = df[df["energy"] >= target_value_si].iloc[0]
    # x1, x2 = row_before["energy"], row_after["energy"]
    # y1, y2 = row_before["counts"], row_after["counts"]
    # interpolated_value_si = y1 + (target_value_si - x1) * (y2 - y1) / (x2 - x1)

    return df


def get_df_ca(class_file: str) -> pd.DataFrame:
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

    # row_before = df[df["energy"] <= target_value_ca].iloc[-1]
    # row_after = df[df["energy"] >= target_value_ca].iloc[0]
    # x1, x2 = row_before["energy"], row_after["energy"]
    # y1, y2 = row_before["counts"], row_after["counts"]
    # interpolated_value_ca = y1 + (target_value_ca - x1) * (y2 - y1) / (x2 - x1)

    return df


def get_df_fe(class_file: str) -> pd.DataFrame:
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

    # row_before = df[df["energy"] <= target_value_fe].iloc[-1]
    # row_after = df[df["energy"] >= target_value_fe].iloc[0]
    # x1, x2 = row_before["energy"], row_after["energy"]
    # y1, y2 = row_before["counts"], row_after["counts"]
    # interpolated_value_fe = y1 + (target_value_fe - x1) * (y2 - y1) / (x2 - x1)

    return df


def get_df_ti(class_file: str) -> pd.DataFrame:
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

    # row_before = df[df["energy"] <= target_value_ti].iloc[-1]
    # row_after = df[df["energy"] >= target_value_ti].iloc[0]
    # x1, x2 = row_before["energy"], row_after["energy"]
    # y1, y2 = row_before["counts"], row_after["counts"]
    # interpolated_value_ti = y1 + (target_value_ti - x1) * (y2 - y1) / (x2 - x1)

    return df


def process_abundance_h(class_file: str) :
    set_xset_settings()

    mg = get_df_mg(class_file)
    al = get_df_al(class_file)
    si = get_df_si(class_file)
    ca = get_df_ca(class_file)
    ti = get_df_ti(class_file)
    fe = get_df_fe(class_file)

    # dict = {
    #     "filename": {"class_file": class_file},
    #     "wt": {"mg": mg, "al": al, "si": si, "ca": ca, "ti": ti, "fe": fe},
    # }
    
    mg_json= mg.to_json(orient="values")
    al_json= al.to_json(orient="values")
    si_json= si.to_json(orient="values")
    fe_json= fe.to_json(orient="values")
    ca_json= ca.to_json(orient="values")
    ti_json= ti.to_json(orient="values")



    return mg_json,al_json,si_json,fe_json,ca_json,ti_json


if __name__ == "__main__":
    dict = process_abundance_h(
        "/home/pg/Documents/Astral-Ray-Scratchpad/Soumik/data/class/-0.04_-5.43.fits"
    )

    print(dict)

