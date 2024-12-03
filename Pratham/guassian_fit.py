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
s1.ignore("0.0-0.9")
s1.ignore("2.0-**")

m1=Model("ga+ga+ga")

# Setting values for Gaussian 1
# Define the model with three Gaussians
# m1 = Model("ga+ga+ga")

# print(m1.componentNames)

# Define the model with three Gaussians
m1 = Model("ga+ga+ga")

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

target_value_mg= 1.25

row_before = df[df['energy'] <= target_value_mg].iloc[-1]  # The row just before the target value
row_after = df[df['energy'] >= target_value_mg].iloc[0] 
x1, x2 = row_before['energy'], row_after['energy']
y1, y2 = row_before['counts'], row_after['counts']
# print(result)
interpolated_value_mg = y1 + (target_value_mg - x1) * (y2 - y1) / (x2 - x1)



target_value_al= 1.49

row_before = df[df['energy'] <= target_value_al].iloc[-1]  # The row just before the target value
row_after = df[df['energy'] >= target_value_al].iloc[0] 
x1, x2 = row_before['energy'], row_after['energy']
y1, y2 = row_before['counts'], row_after['counts']
# print(result)
interpolated_value_al = y1 + (target_value_al - x1) * (y2 - y1) / (x2 - x1)


target_value_si= 1.74

row_before = df[df['energy'] <= target_value_si].iloc[-1]  # The row just before the target value
row_after = df[df['energy'] >= target_value_si].iloc[0] 
x1, x2 = row_before['energy'], row_after['energy']
y1, y2 = row_before['counts'], row_after['counts']
# print(result)
interpolated_value_si = y1 + (target_value_si - x1) * (y2 - y1) / (x2 - x1)
print(f"Mg/Si : {interpolated_value_mg/interpolated_value_si}")
      
print(f"Al/Si : {interpolated_value_al/interpolated_value_si}")


# avg_row=row['counts'].mean()

# Plot.show("area")