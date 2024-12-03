from xspec import * 
import os
import pandas as pd

s1=Spectrum("ch2_cla_l1_20210827T210316000_20210827T210332000_1024.fits", backFile='USE_DEFAULT',respFile='USE_DEFAULT',
arfFile='USE_DEFAULT')

s1.background=("background_rebinned_2_2.fits")

# Plot.device="/xw"
# s1.response.rmf("class_rmf_v1.rmf")
# s1.response.arf("class_rmf_v1.arf")


# Plot.background=False

# s1.notice("1.0-10.0")
s1.ignore("0.0-3.2")
s1.ignore("4.2-**")

m1=Model("ga")

# Setting values for Gaussian 1
# Define the model with three Gaussians
# m1 = Model("ga+ga+ga")

# print(m1.componentNames)

# Define the model with three Gaussians


# Setting values for Gaussian 1
m1.gaussian.LineE = 3.69  # LineE for Gaussian 1 (in keV)
m1.gaussian.Sigma = 0.05   # Sigma for Gaussian 1 (in keV)
m1.gaussian.norm = 1       # Norm for Gaussian 1
m1.gaussian.LineE.frozen=True

# Fit.nIterations=10
Fit.perform()
# # os.system("y")

Plot.device="/xs"
Plot.area=True
Plot.xAxis="KeV"


# PlotManager.setplot("area",True)
# s1.areaScale()
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
# df.to_csv('weird_1.csv', index=False)
# If you are searching for a value close to 1.49 in Column 2


# result_al = df[df['energy'].between(1.47, 1.51)]

target_value_ca= 3.69

row_before = df[df['energy'] <= target_value_ca].iloc[-1]  # The row just before the target value
row_after = df[df['energy'] >= target_value_ca].iloc[0] 
x1, x2 = row_before['energy'], row_after['energy']
y1, y2 = row_before['counts'], row_after['counts']
# print(result)
interpolated_value_ca= y1 + (target_value_ca - x1) * (y2 - y1) / (x2 - x1)

print(interpolated_value_ca)

# avg_row=row['counts'].mean()

# Plot.show("area")
