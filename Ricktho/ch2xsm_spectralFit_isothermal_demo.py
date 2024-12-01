from xspec import *

from datetime import datetime
import os
import numpy as np
from astropy.io import fits
import corner
import matplotlib.pyplot as plt


AllData.clear()
AllModels.clear()

tref = datetime(2017, 1, 1)
tstart = (datetime(2021, 8, 27, 21, 3, 16) - tref).total_seconds()
tstop = (datetime(2021, 8, 27, 21, 3, 32) - tref).total_seconds()

l1dir = "xsm/raw/"
l2dir = "xsm/calibrated/"

base = "ch2_xsm_20210827_v1"

l1file = l1dir + "/" + base + "_level1.fits"
hkfile = l1dir + "/" + base + "_level1.hk"
safile = l1dir + "/" + base + "_level1.sa"
gtifile = l2dir + "/" + base + "_level2.gti"

specbase = "ch2_xsm_20240711_21316-21332"
specfile = specbase + ".pha"

genspec_command = (
    "xsmgenspec l1file="
    + l1file
    + " specfile="
    + specfile
    + " spectype='time-integrated'"
    + " tstart="
    + str(tstart)
    + " tstop="
    + str(tstop)
    + " hkfile="
    + hkfile
    + " safile="
    + safile
    + " gtifile="
    + gtifile
)

s = os.system(genspec_command)
# Load spectrum (ARF, RMF, background etc will be loaded automatically if specified in spectrum header)
spec = Spectrum(specfile)
Plot.device = "/xw"
Plot.xAxis = "keV"
Plot("ld")
# We need to ignore spectrum below 1.3 keV (response not well known) and above 4.2 keV where there are not many counts above background, before proceeding to spectral fitting.
spec.ignore("**-1.3 4.2-**")
Plot("ld")

basepathmod = "/home/rick/chspec/"
AllModels.lmod("chspec", dirPath=basepathmod)
m1 = Model("chisoth")

Fit.perform()
Plot("ld", "delc")

# Another way to access the model object, and parameters
# m1==Allmode
m1(12).frozen = False
m1(14).frozen = False
m1(16).frozen = False

Fit.perform()
Plot("ld", "delc")
AllModels.show(parIDs="1 12 14 16 31")
Fit.query = "yes"
# Fit.error("1.0 1 12 14 16 31")

fxcm = "new_chisoth_Fit.xcm"
Xset.save(fxcm)

Plot("ld", "delc")

ene = Plot.x(plotGroup=1, plotWindow=1)
eneErr = Plot.xErr(plotGroup=1, plotWindow=1)
spec = Plot.y(plotGroup=1, plotWindow=1)
specErr = Plot.yErr(plotGroup=1, plotWindow=1)
ascii_filename = "solar_spectrum_data.txt"

# Convert the rate (counts/s/keV) to photons/(s cm^2 keV) as needed
# Assuming an area factor is used (modify this if there's specific calibration needed)
area_factor = 20  # Replace this with the actual conversion factor if needed

# Prepare data for saving
with open(ascii_filename, "w") as file:
    file.write("# Energy (keV)   Energy Error (keV)   Solar Spectrum (photons/(s cm2 keV))\n")
    for i in range(len(ene)):
        energy = ene[i]
        energy_error = eneErr[i]
        spectrum_value = spec[i] / area_factor  # Adjust with an area factor if applicable

        file.write(f"{energy:.5f}   {energy_error:.5f}   {spectrum_value:.5e}\n")

print(f"Data saved to {ascii_filename}")
fitmodel = Plot.model(plotGroup=1, plotWindow=1)

delchi = Plot.y(plotGroup=1, plotWindow=2)
delchiErr = Plot.yErr(plotGroup=1, plotWindow=2)

fig0 = plt.figure(num=None, figsize=(6, 4), facecolor="w", edgecolor="k")

ax0 = fig0.add_axes([0.15, 0.4, 0.8, 0.55])
ax0.xaxis.set_visible(False)
plt.errorbar(ene, spec, xerr=eneErr, yerr=specErr, fmt=".", ms=0.5, capsize=1.0, lw=0.8)
plt.step(ene, fitmodel, where="mid")
plt.yscale("log")
plt.xscale("log")
plt.xlim([1.3, 4.5])
plt.ylim([0.1, 1e3])
plt.ylabel("Rate (counts s$^{-1}$ keV$^{-1}$)")


ax1 = fig0.add_axes([0.15, 0.15, 0.8, 0.25])
plt.axhline(0, linestyle="dashed", color="black")
plt.errorbar(ene, delchi, xerr=eneErr, yerr=delchiErr, fmt=".", ms=0.1, capsize=1.0, lw=0.8)
plt.xscale("log")
plt.xlim([1.3, 4.5])
plt.ylabel("$\Delta \chi$")

plt.xlabel("Energy (keV)")


plt.show()
plt.close()
