from typing import Tuple, Optional, List, Dict
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


def model_to_model_plot(model: list) -> List[Dict[str, float]]:
    model_plot = list()
    for idx, h in enumerate(model):
        model_plot.append({"channelNumber": idx + 1, "count": h})

    return model_plot


def fit(return_model: bool = False, plot_device: str = "/null") -> Tuple[float, float, Optional[List]]:
    Xset.allowPrompting = False
    Fit.nIterations = 1000
    Fit.perform()

    if not return_model:
        return Fit.statistic, Fit.dof, None

    Plot.device = plot_device
    Plot("model")

    return Fit.statistic, Fit.dof, model_to_model_plot(Plot.model())


def fit_and_plot(plot_device: str = "/null") -> Tuple[DataFrame, float, float]:
    Xset.allowPrompting = False
    Fit.nIterations = 1000
    Fit.perform()

    Plot.device = plot_device
    Plot.area = False
    Plot.xAxis = "KeV"

    Plot("data", "resid")
    chi_2 = Fit.statistic
    dof = Fit.dof
    xVals = Plot.x()
    yVals = Plot.y()

    return DataFrame({"energy": xVals, "counts": yVals}), chi_2, dof
