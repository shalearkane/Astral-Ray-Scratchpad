from typing import Tuple
from helpers.xset_settings import reset_xspec, fit_and_plot, set_xset_settings
from xspec import Spectrum, Model

bin_factor = 2048
arfFile = f"model/data/{bin_factor}/class_arf_v1.arf"
respFile = f"model/data/{bin_factor}/class_rmf_v1.rmf"
background = "model/data/reference/background_allevents.fits"


def get_df_al_si_mg(class_file: str) -> Tuple[float, float, float]:
    reset_xspec()

    s1 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s1.ignore("0.0-0.9")
    s1.ignore("2.0-**")
    m1 = Model("ga+ga+ga")

    # Setting values for Gaussian 1
    m1.gaussian.LineE = 1.25  # type: ignore
    m1.gaussian.Sigma = 0.05  # type: ignore
    m1.gaussian.norm = 1  # type: ignore
    m1.gaussian.LineE.frozen = True  # type: ignore
    # Setting values for Gaussian 2
    m1.gaussian_2.LineE = 1.48  # type: ignore
    m1.gaussian_2.Sigma = 0.05  # type: ignore
    m1.gaussian_2.norm = 1  # type: ignore
    m1.gaussian_2.LineE.frozen = True  # type: ignore
    # Setting values for Gaussian 3
    m1.gaussian_3.LineE = 1.74  # type: ignore
    m1.gaussian_3.Sigma = 0.05  # type: ignore
    m1.gaussian_3.norm = 1  # type: ignore
    m1.gaussian_3.LineE.frozen = True  # type: ignore

    df = fit_and_plot()

    target_value_mg = 1.25

    row_before = df[df["energy"] <= target_value_mg].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_mg].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_mg = y1 + (target_value_mg - x1) * (y2 - y1) / (x2 - x1)

    target_value_al = 1.49

    row_before = df[df["energy"] <= target_value_al].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_al].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]
    # print(result)
    interpolated_value_al = y1 + (target_value_al - x1) * (y2 - y1) / (x2 - x1)

    target_value_si = 1.74

    row_before = df[df["energy"] <= target_value_si].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_si].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]

    interpolated_value_si = y1 + (target_value_si - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_mg, interpolated_value_al, interpolated_value_si

def get_df_mg(class_file: str) -> float:
    reset_xspec()

    s2 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-1.1")
    s2.ignore("1.37-**")
    m2 = Model("ga")

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 1.25  # type: ignore
    m2.gaussian.Sigma = 0.05  # type: ignore
    m2.gaussian.norm = 1  # type: ignore
    m2.gaussian.LineE.frozen = True  # type: ignore

    df = fit_and_plot()

    target_value_mg = 1.25

    row_before = df[df["energy"] <= target_value_mg].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_mg].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_mg = y1 + (target_value_mg - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_mg




def get_df_al(class_file: str) -> float:
    reset_xspec()

    s2 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-1.37")
    s2.ignore("1.62-**")
    m2 = Model("ga")

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 1.49  # type: ignore
    m2.gaussian.Sigma = 0.05  # type: ignore
    m2.gaussian.norm = 1  # type: ignore
    m2.gaussian.LineE.frozen = True  # type: ignore

    df = fit_and_plot()

    target_value_al = 1.49

    row_before = df[df["energy"] <= target_value_al].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_al].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_al = y1 + (target_value_al - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_al




def get_df_si(class_file: str) -> float:
    reset_xspec()

    s2 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-1.62")
    s2.ignore("1.9-**")
    m2 = Model("ga")

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 1.74  # type: ignore
    m2.gaussian.Sigma = 0.05  # type: ignore
    m2.gaussian.norm = 1  # type: ignore
    m2.gaussian.LineE.frozen = True  # type: ignore

    df = fit_and_plot()

    target_value_si = 1.74

    row_before = df[df["energy"] <= target_value_si].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_si].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_si = y1 + (target_value_si - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_si


def get_df_ti(class_file: str) -> float:
    reset_xspec()

    s2 = Spectrum(class_file, backFile=background, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-4.3")
    s2.ignore("4.7-**")
    m2 = Model("ga")

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 4.51  # type: ignore
    m2.gaussian.Sigma = 0.05  # type: ignore
    m2.gaussian.norm = 1  # type: ignore
    m2.gaussian.LineE.frozen = True  # type: ignore

    df = fit_and_plot()

    target_value_ti = 4.51

    row_before = df[df["energy"] <= target_value_ti].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_ti].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_ti = y1 + (target_value_ti - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_ti




def get_df_ca(class_file: str) -> float:
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

    df = fit_and_plot()

    target_value_ca = 3.69

    row_before = df[df["energy"] <= target_value_ca].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_ca].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_ca = y1 + (target_value_ca - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_ca


def get_df_fe(class_file: str) -> float:
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

    df = fit_and_plot()

    target_value_fe = 6.40

    row_before = df[df["energy"] <= target_value_fe].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_fe].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_fe = y1 + (target_value_fe - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_fe


def process_abundance_h(class_file: str):
    set_xset_settings()
    mg, al, si = get_df_al_si_mg(class_file)
    mg = get_df_mg
    al = get_df_al
    si = get_df_si
    ti = get_df_ti
    ca = get_df_ca(class_file)
    fe = get_df_fe(class_file)

    dict = {"filename": class_file, "wt": {"Wt_Mg": mg, "Wt_Al": al, "Wt_Si": si, "Wt_Ca": ca, "Wt_Fe": fe}}

    return dict


if __name__ == "__main__":
    dict = process_abundance_h("/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data/class/ch2_cla_l1_20191022T112444865_20191022T112452865.fits")

    print(dict)
