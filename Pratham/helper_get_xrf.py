from xspec import * 
import os
import pandas as pd


def get_df_al_si_mg( class_file:str,bck:str): 

    Xset.allowPrompting = False
    Xset.chatter = 0
    s1=Spectrum(class_file, backFile='USE_DEFAULT',respFile='USE_DEFAULT',arfFile='USE_DEFAULT')
    s1.background=(bck)
    s1.ignore("0.0-0.9")
    s1.ignore("2.0-**")
    m1=Model("ga+ga+ga")
    # m1 = Model("ga+ga+ga")

    # Setting values for Gaussian 1
    m1.gaussian.LineE = 1.25  # LineE for Gaussian 1 (in keV)
    m1.gaussian.Sigma = 0.05   # Sigma for Gaussian 1 (in keV)
    m1.gaussian.norm = 1       # Norm for Gaussian 1
    m1.gaussian.LineE.frozen=True
    # Setting values for Gaussian 2
    m1.gaussian_2.LineE = 1.49  # LineE for Gaussian 2 (in keV)
    m1.gaussian_2.Sigma = 0.05   # Sigma for Gaussian 2 (in keV)
    m1.gaussian_2.norm = 1       # Norm for Gaussian 2
    m1.gaussian_2.LineE.frozen=True
    # Setting values for Gaussian 3
    m1.gaussian_3.LineE = 1.74  # LineE for Gaussian 3 (in keV)
    m1.gaussian_3.Sigma = 0.05   # Sigma for Gaussian 3 (in keV)
    m1.gaussian_3.norm = 1       # Norm for Gaussian 3
    m1.gaussian_3.LineE.frozen=True


    Fit.perform()


    Plot.device="/xs"
    Plot.area=True
    Plot.xAxis="KeV"


    # Plot("data", "resid")

    xVals=Plot.x()
    yVals=Plot.y()

    df = pd.DataFrame({
    'energy': xVals,
    'counts': yVals})

    target_value_mg= 1.25

    row_before = df[df['energy'] <= target_value_mg].iloc[-1]  # The row just before the target value
    row_after = df[df['energy'] >= target_value_mg].iloc[0] 
    x1, x2 = row_before['energy'], row_after['energy']
    y1, y2 = row_before['counts'], row_after['counts']# print(result)
    interpolated_value_mg = y1 + (target_value_mg - x1) * (y2 - y1) / (x2 - x1)



    target_value_al= 1.49

    row_before = df[df['energy'] <= target_value_al].iloc[-1]  # The row just before the target value
    row_after = df[df['energy'] >= target_value_al].iloc[0] 
    x1, x2 = row_before['energy'], row_after['energy']
    y1,y2 = row_before['counts'], row_after['counts']
    # print(result)
    interpolated_value_al = y1 + (target_value_al - x1) * (y2 - y1) / (x2 - x1)


    target_value_si= 1.74

    row_before = df[df['energy'] <= target_value_si].iloc[-1]  # The row just before the target value
    row_after = df[df['energy'] >= target_value_si].iloc[0] 
    x1, x2 = row_before['energy'], row_after['energy']
    y1, y2 = row_before['counts'], row_after['counts']
    # print(result)
    interpolated_value_si = y1 + (target_value_si - x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_mg,interpolated_value_al,interpolated_value_si


def get_df_ca( class_file:str,bck:str): 

    Xset.allowPrompting = False
    Xset.chatter = 0
    s1=Spectrum(class_file, backFile='USE_DEFAULT',respFile='USE_DEFAULT',arfFile='USE_DEFAULT')
    s1.background=(bck)
    s1.ignore("0.0-3.2")
    s1.ignore("4.2-**")
    m1=Model("ga")
    

    # Setting values for Gaussian 1
    m1.gaussian.LineE = 3.69  # LineE for Gaussian 1 (in keV)
    m1.gaussian.Sigma = 0.05   # Sigma for Gaussian 1 (in keV)
    m1.gaussian.norm = 1       # Norm for Gaussian 1
    m1.gaussian.LineE.frozen=True
    


    Fit.perform()


    Plot.device="/xs"
    Plot.area=True
    Plot.xAxis="KeV"


    # Plot("data", "resid")

    xVals=Plot.x()
    yVals=Plot.y()

    df = pd.DataFrame({
    'energy': xVals,
    'counts': yVals})

    target_value_ca= 3.69

    row_before = df[df['energy'] <= target_value_ca].iloc[-1]  # The row just before the target value
    row_after = df[df['energy'] >= target_value_ca].iloc[0] 
    x1, x2 = row_before['energy'], row_after['energy']
    y1, y2 = row_before['counts'], row_after['counts']# print(result)
    interpolated_value_ca = y1 + (target_value_ca- x1) * (y2 - y1) / (x2 - x1)

    return interpolated_value_ca

def dict_mg_al_si_ca(class_file:str,bck:str):
    mg,al,si=get_df_al_si_mg(class_file,bck)
    ca=get_df_ca(class_file,bck)

    dict={"filename": class_file , "Wt_Mg":mg, "Wt_Al":al,"Wt_Si":si,"Wt_Ca":ca}

    return dict







    
    


    


    



