from xspec import * 
import os
import pandas as pd
s1=Spectrum("ch2_cla_l1_20210827T210316000_20210827T210332000_1024.fits")

s1.background=("background_rebinned_2_2.fits")

# Plot.device="/xw"
# s1.response.rmf("class_rmf_v1.rmf")
# s1.response.arf("class_rmf_v1.arf")


# Plot.background=False

# s1.notice("1.0-10.0")
s1.ignore("0.0-0.9")
s1.ignore("10.0-**")

m1=Model("ga+ga+ga")

# Setting values for Gaussian 1
# Define the model with three Gaussians
m1 = Model("ga+ga+ga")

# print(m1.componentNames)

# Define the model with three Gaussians
m1 = Model("ga+ga+ga")

# Setting values for Gaussian 1
m1.gaussian.LineE = 1.25   # LineE for Gaussian 1 (in keV)
m1.gaussian.Sigma = 0.05   # Sigma for Gaussian 1 (in keV)
m1.gaussian.norm = 1       # Norm for Gaussian 1

# Setting values for Gaussian 2
m1.gaussian_2.LineE = 1.49   # LineE for Gaussian 2 (in keV)
m1.gaussian_2.Sigma = 0.05   # Sigma for Gaussian 2 (in keV)
m1.gaussian_2.norm = 1       # Norm for Gaussian 2

# Setting values for Gaussian 3
m1.gaussian_3.LineE = 1.74   # LineE for Gaussian 3 (in keV)
m1.gaussian_3.Sigma = 0.05   # Sigma for Gaussian 3 (in keV)
m1.gaussian_3.norm = 1       # Norm for Gaussian 3

# Fit.nIterations=10
Fit.perform()
# os.system("y")

Plot.device="/xs"
Plot.xAxis="KeV"
Plot("data", "resid")

xVals=Plot.x()
yVals=Plot.y()

# print(len(xVals)==len(yVals))

df = pd.DataFrame({
    'energy': xVals,
    'counts': yVals
})
# val1=df[['energy']==1.49]
# print(val1)
df.to_csv('weird_1.csv', index=False)