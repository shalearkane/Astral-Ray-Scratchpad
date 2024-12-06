from xspec import Xset, AllData, AllModels, AllChains, Fit, Plot
from pandas import DataFrame


def set_xset_settings(parallelism: int = 2):
    Xset.chatter = 0
    Xset.allowPrompting = False
    Xset.parallel.error = parallelism
    Xset.parallel.goodness = parallelism
    Xset.parallel.leven = parallelism
    Xset.parallel.steppar = parallelism
    Xset.parallel.walkers = parallelism


def reset_xspec():
    AllData.clear()
    AllModels.clear()
    AllChains.clear()


def fit_and_plot(plot_device: str = "/null") -> DataFrame:
    Xset.allowPrompting = False
    Fit.nIterations = 1000
    Fit.perform()

    Plot.device = plot_device
    Plot.area = False
    Plot.xAxis = "KeV"

    Plot("data", "resid")
    chi_2=Fit.statistic
    dof=Fit.dof
    xVals = Plot.x()
    yVals = Plot.y()

    return DataFrame({"energy": xVals, "counts": yVals,"Chi_2":chi_2,"dof":dof})
