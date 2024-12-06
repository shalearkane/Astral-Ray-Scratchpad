from xspec import *
import os
import pandas as pd

arfFile = "/home/pg/Documents/Astral-Ray-Scratchpad/Soumik/model/data/1024/class_arf_v1.arf"
respFile = "/home/pg/Documents/Astral-Ray-Scratchpad/Soumik/model/data/1024/class_rmf_v1.rmf"
# Xset.allowPrompting = False
# num_parallel_param = 8
# Xset.parallel.error = num_parallel_param
# Xset.parallel.goodness = num_parallel_param
# Xset.parallel.leven = num_parallel_param
# Xset.parallel.steppar = num_parallel_param
# Xset.parallel.walkers = num_parallel_param



# def get_df_al_si_mg(class_file: str, bck: str):

#     Xset.allowPrompting = False
#     s1 = Spectrum(class_file, backFile=bck, respFile=respFile, arfFile=arfFile)
#     s1.ignore("0.0-0.9")
#     s1.ignore("2.0-**")
#     m1 = Model("ga+ga+ga")
#     m1 = Model("ga+ga+ga")

#     # Setting values for Gaussian 1
#     m1.gaussian.LineE = 1.25  # LineE for Gaussian 1 (in keV)
#     m1.gaussian.Sigma = 0.05  # Sigma for Gaussian 1 (in keV)
#     m1.gaussian.norm = 1  # Norm for Gaussian 1
#     m1.gaussian.LineE.frozen = True
#     # Setting values for Gaussian 2
#     m1.gaussian_2.LineE = 1.48  # LineE for Gaussian 2 (in keV)
#     m1.gaussian_2.Sigma = 0.05  # Sigma for Gaussian 2 (in keV)
#     m1.gaussian_2.norm = 1  # Norm for Gaussian 2
#     m1.gaussian_2.LineE.frozen = True
#     # Setting values for Gaussian 3
#     m1.gaussian_3.LineE = 1.74  # LineE for Gaussian 3 (in keV)
#     m1.gaussian_3.Sigma = 0.05  # Sigma for Gaussian 3 (in keV)
#     m1.gaussian_3.norm = 1  # Norm for Gaussian 3
#     m1.gaussian_3.LineE.frozen = True

#     Fit.perform()

#     Plot.device = "/xs"
#     Plot.area = True
#     Plot.xAxis = "KeV"

#     Plot("data", "resid")
    

#     xVals = Plot.x()
#     yVals = Plot.y()

#     df = pd.DataFrame({"energy": xVals, "counts": yVals})

#     target_value_mg = 1.25

#     row_before = df[df["energy"] <= target_value_mg].iloc[-1]  # The row just before the target value
#     row_after = df[df["energy"] >= target_value_mg].iloc[0]
#     x1, x2 = row_before["energy"], row_after["energy"]
#     y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
#     interpolated_value_mg = y1 + (target_value_mg - x1) * (y2 - y1) / (x2 - x1)

#     target_value_al = 1.49

#     row_before = df[df["energy"] <= target_value_al].iloc[-1]  # The row just before the target value
#     row_after = df[df["energy"] >= target_value_al].iloc[0]
#     x1, x2 = row_before["energy"], row_after["energy"]
#     y1, y2 = row_before["counts"], row_after["counts"]
#     # print(result)
#     interpolated_value_al = y1 + (target_value_al - x1) * (y2 - y1) / (x2 - x1)

#     target_value_si = 1.74

#     row_before = df[df["energy"] <= target_value_si].iloc[-1]  # The row just before the target value
#     row_after = df[df["energy"] >= target_value_si].iloc[0]
#     x1, x2 = row_before["energy"], row_after["energy"]
#     y1, y2 = row_before["counts"], row_after["counts"]
#     # print(result)
#     interpolated_value_si = y1 + (target_value_si - x1) * (y2 - y1) / (x2 - x1)
#     # Plot.commands=()


#     return interpolated_value_mg, interpolated_value_al, interpolated_value_si

def get_df_mg(class_file: str, bck: str):

    Xset.allowPrompting = False
    AllData.clear()
    AllModels.clear()
    s2 = Spectrum(class_file, backFile=bck, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-1.10")
    s2.ignore("1.37-**")
    m2 = Model("ga")

    

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 1.25  # LineE for Gaussian 1 (in keV)
    m2.gaussian.Sigma = 0.05  # Sigma for Gaussian 1 (in keV)
    m2.gaussian.norm = 1  # Norm for Gaussian 1
    m2.gaussian.LineE.frozen = True

    Fit.perform()

    Plot.device = "/xs"
    Plot.area = True
    Plot.xAxis = "KeV"

    Plot("data", "resid")

    xVals = Plot.x()
    yVals = Plot.y()

    df = pd.DataFrame({"energy": xVals, "counts": yVals})
    
    target_value_mg = 1.25

    row_before = df[df["energy"] <= target_value_mg].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_mg].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_mg = y1 + (target_value_mg - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_mg




def get_df_al(class_file: str, bck: str):

    Xset.allowPrompting = False
    AllData.clear()
    AllModels.clear()
    s2 = Spectrum(class_file, backFile=bck, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-1.37")
    s2.ignore("1.62-**")
    m2 = Model("ga")

    

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 1.49  # LineE for Gaussian 1 (in keV)
    m2.gaussian.Sigma = 0.05  # Sigma for Gaussian 1 (in keV)
    m2.gaussian.norm = 1  # Norm for Gaussian 1
    m2.gaussian.LineE.frozen = True

    Fit.perform()

    Plot.device = "/xs"
    Plot.area = True
    Plot.xAxis = "KeV"

    Plot("data", "resid")

    xVals = Plot.x()
    yVals = Plot.y()

    df = pd.DataFrame({"energy": xVals, "counts": yVals})
    
    target_value_al = 1.49

    row_before = df[df["energy"] <= target_value_al].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_al].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_al = y1 + (target_value_al - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_al



def get_df_si(class_file: str, bck: str):

    Xset.allowPrompting = False
    AllData.clear()
    AllModels.clear()
    s2 = Spectrum(class_file, backFile=bck, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-1.62")
    s2.ignore("1.9-**")
    m2 = Model("ga")

    

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 1.74  # LineE for Gaussian 1 (in keV)
    m2.gaussian.Sigma = 0.05  # Sigma for Gaussian 1 (in keV)
    m2.gaussian.norm = 1  # Norm for Gaussian 1
    m2.gaussian.LineE.frozen = True

    Fit.perform()

    Plot.device = "/xs"
    Plot.area = True
    Plot.xAxis = "KeV"

    Plot("data", "resid")

    xVals = Plot.x()
    yVals = Plot.y()

    df = pd.DataFrame({"energy": xVals, "counts": yVals})
    
    target_value_si = 1.74

    row_before = df[df["energy"] <= target_value_si].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_si].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_si = y1 + (target_value_si - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_si



def get_df_ca(class_file: str, bck: str):

    Xset.allowPrompting = False
    AllData.clear()
    AllModels.clear()
    s2 = Spectrum(class_file, backFile=bck, respFile=respFile, arfFile=arfFile)
    s2.ignore("0.0-3.2")
    s2.ignore("4.2-**")
    m2 = Model("ga")

    

    # Setting values for Gaussian 1
    m2.gaussian.LineE = 3.69  # LineE for Gaussian 1 (in keV)
    m2.gaussian.Sigma = 0.05  # Sigma for Gaussian 1 (in keV)
    m2.gaussian.norm = 1  # Norm for Gaussian 1
    m2.gaussian.LineE.frozen = True

    Fit.perform()

    Plot.device = "/xs"
    Plot.area = True
    Plot.xAxis = "KeV"

    Plot("data", "resid")

    xVals = Plot.x()
    yVals = Plot.y()

    df = pd.DataFrame({"energy": xVals, "counts": yVals})
    
    target_value_ca = 3.69

    row_before = df[df["energy"] <= target_value_ca].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_ca].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_ca = y1 + (target_value_ca - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_ca


def get_df_fe(class_file: str, bck: str):

    Xset.allowPrompting = False
    AllData.clear()
    AllModels.clear()
    s3 = Spectrum(class_file, backFile=bck, respFile=respFile, arfFile=arfFile)
    s3.ignore("0.0-6.1")
    s3.ignore("6.6-**")
    m3 = Model("ga")

    # Setting values for Gaussian 1
    m3.gaussian.LineE = 6.40  # LineE for Gaussian 1 (in keV)
    m3.gaussian.Sigma = 0.05  # Sigma for Gaussian 1 (in keV)
    m3.gaussian.norm = 1  # Norm for Gaussian 1
    m3.gaussian.LineE.frozen = True

    Fit.perform()

    Plot.device = "/xs"
    Plot.area = True
    Plot.xAxis = "KeV"

    Plot("data", "resid")

    xVals = Plot.x()
    yVals = Plot.y()

    df = pd.DataFrame({"energy": xVals, "counts": yVals})

    target_value_fe = 6.40
    
    row_before = df[df["energy"] <= target_value_fe].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_fe].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_fe = y1 + (target_value_fe - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_fe

def get_df_ti(class_file: str, bck: str):

    Xset.allowPrompting = False
    AllData.clear()
    AllModels.clear()
    s3 = Spectrum(class_file, backFile=bck, respFile=respFile, arfFile=arfFile)
    s3.ignore("0.0-4.2")
    s3.ignore("5.0-**")
    m3 = Model("ga")

    # Setting values for Gaussian 1
    m3.gaussian.LineE = 4.51  # LineE for Gaussian 1 (in keV)
    m3.gaussian.Sigma = 0.05  # Sigma for Gaussian 1 (in keV)
    m3.gaussian.norm = 1  # Norm for Gaussian 1
    m3.gaussian.LineE.frozen = True

    Fit.perform()

    Plot.device = "/xs"
    Plot.area = True
    Plot.xAxis = "KeV"

    Plot("data", "resid")

    xVals = Plot.x()
    yVals = Plot.y()

    df = pd.DataFrame({"energy": xVals, "counts": yVals})

    target_value_ti = 4.51
    
    row_before = df[df["energy"] <= target_value_ti].iloc[-1]  # The row just before the target value
    row_after = df[df["energy"] >= target_value_ti].iloc[0]
    x1, x2 = row_before["energy"], row_after["energy"]
    y1, y2 = row_before["counts"], row_after["counts"]  # print(result)
    interpolated_value_ti = y1 + (target_value_ti - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_ti


def dict_mg_al_si_ca(class_file: str, bck: str):
    # mg, al, si = get_df_al_si_mg(class_file, bck)
    # AllData.clear()
    # AllModels.clear()
    ca = get_df_ca(class_file, bck)
    AllData.clear()
    AllModels.clear()
    fe = get_df_fe(class_file, bck)
    AllData.clear()
    AllModels.clear()
    ti=get_df_ti(class_file,bck)
    AllData.clear()
    AllModels.clear()

    mg = get_df_mg(class_file, bck)
    AllData.clear()
    AllModels.clear()
    al = get_df_al(class_file, bck)
    AllData.clear()
    AllModels.clear()
    si = get_df_si(class_file, bck)


    dict = {"filename": class_file, "Wt_Mg": mg, "Wt_Al": al, "Wt_Si": si, "Wt_Ca": ca, "Wt_Fe": fe,"Wt_Ti":ti}

    return dict


print(dict_mg_al_si_ca("ch2_cla_l1_20210827T210316000_20210827T210332000_1024.fits", "background_rebinned_2_2.fits"))
