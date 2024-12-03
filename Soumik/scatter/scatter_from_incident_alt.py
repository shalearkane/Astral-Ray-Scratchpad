import pandas as pd
import numpy as np
from scatter_from_incident import load_incident_spectrum

param_1 = [1.64928289e-10, 8.73922596e-01]
param_2 = [5.96908953e-10, 4.75183036e-01]
param_3 = [3.23902852e-09, 2.45369568e-01]


def get_scatter(region: pd.DataFrame, n: int):
    if n == 1:
        region["INTPSPEC"] = region["Intensity"] * param_1[0] * np.exp(param_1[1] * region["keV"])
        return region

    if n == 2:
        region["INTPSPEC"] = region["Intensity"] * param_2[0] * np.exp(param_2[1] * region["keV"])
        return region

    if n == 3:
        region["INTPSPEC"] = region["Intensity"] * param_3[0] * np.exp(param_3[1] * region["keV"])
        return region


def scatter_from_incident_alt(incident_solar_file: str) -> pd.DataFrame:
    incident_solar_df = load_incident_spectrum(incident_solar_file)
    region_1 = incident_solar_df[incident_solar_df["keV"] < 4]
    region_2 = incident_solar_df[(incident_solar_df["keV"] >= 4) & (incident_solar_df["keV"] <= 7.10)]
    region_3 = incident_solar_df[(incident_solar_df["keV"] >= 7.10) & (incident_solar_df["keV"] <= 15)]

    region_1 = get_scatter(region_1, 1)
    region_2 = get_scatter(region_2, 2)
    region_3 = get_scatter(region_3, 3)

    result = pd.concat([region_1, region_2, region_3], axis=0, ignore_index=True)
    result_df = result[["keV", "INTPSPEC"]]

    return result_df
