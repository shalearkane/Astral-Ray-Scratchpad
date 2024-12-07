import pandas as pd
import numpy as np
import matplotlib
from typing import List
from pandas import DataFrame
import json

import matplotlib.pyplot as plt
import os

matplotlib.use("Agg")


def json_to_df(json_file_path: str, elements: List[str] = ["na", "mg", "al", "si", "ca", "ti", "fe"]) -> pd.DataFrame:
    with open(json_file_path, "r") as file:
        data_list = json.load(file)

    records = []

    for data in data_list:
        record = {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "solar_zenith_angle": data["computed_metadata"]["solar_zenith_angle"],
            "emission_angle": data["computed_metadata"]["emission_angle"],
            "solar_zenith_angle_cosec": data["computed_metadata"]["solar_zenith_angle_cosec"],
            "emission_angle_cosec": data["computed_metadata"]["emission_angle_cosec"],
            "altitude": data["computed_metadata"]["altitude"],
            "exposure": data["computed_metadata"]["exposure"],
            "mid_utc": data["computed_metadata"]["mid_utc"],
            "photon_count": data["photon_count"],
        }

        for element, wt in data["wt"].items():
            record[f"wt_{element}"] = wt

        for element, chi in data["chi_2"].items():
            record[f"chi_2_{element}"] = chi

        for element, dof in data["dof"].items():
            record[f"dof_{element}"] = dof

        for element in elements:
            record[f"peak_{element}_h"] = data["computed_metadata"].get(f"peak_{element}_h", 0)
            record[f"peak_{element}_c"] = data["computed_metadata"].get(f"peak_{element}_c", 0)

        records.append(record)

    df = pd.DataFrame(records)

    return df


def filter_by_peak_counts(df: DataFrame, si_peak_col: str, percentage: float, peak_columns: List[str]) -> DataFrame:
    threshold: float = percentage / 100.0
    for col in peak_columns:
        df = df[df[col] >= df[si_peak_col] * threshold]

    return df


def plot_prediction_ratio(
    df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    element_col: str,
    save_dir: str,
    cmap: str = "viridis",
    point_size: float = 50,
) -> None:
    df["element"] = df[element_col]

    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(
        df[lon_col],
        df[lat_col],
        c=df["element"],
        s=point_size,
        cmap=cmap,
        edgecolors="none",
        alpha=1,
    )
    plt.colorbar(scatter, label=f"Model Prediction for {element_col} ")
    plt.title(f"Scatter Plot of Model {element_col} ", fontsize=16)
    plt.xlabel("Longitude", fontsize=14)
    plt.ylabel("Latitude", fontsize=14)
    plt.tight_layout()
    file_name = f"model_predict_{element_col}_scatter_plot.png"
    save_path = os.path.join(save_dir, file_name)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Scatter plot saved at {save_path}")


def plot_raw_xrf_lines(
    input_json: str,
    plot_save_dir: str,
    si_peak_col: str = "peak_si_c",
    peak_columns: List[str] = ["peak_mg_c", "peak_al_c", "peak_ca_c", "peak_ti_c", "peak_fe_c"],
    filter_percentage: float = 50,
    bins: int = 50,
    cmap: str = "viridis",
) -> None:
    df = json_to_df(input_json)

    elements: List[str] = ["ca", "mg", "al", "ti", "fe"]
    for element in elements:
        df[f"wt_{element}_si_ratio"] = df[f"wt_{element}"] / df["wt_si"]
        df.drop(columns=[f"wt_{element}"], inplace=True)

    df.drop(columns=["wt_si"], inplace=True)

    for element in elements:
        df[f"chi_2_{element}_si_ratio"] = df[[f"chi_2_{element}", "chi_2_si"]].max(axis=1)
        df[f"dof_{element}_si_ratio"] = df[[f"dof_{element}", "dof_si"]].min(axis=1)
        df.drop(columns=[f"chi_2_{element}", f"dof_{element}"], inplace=True)

    df.drop(columns=["chi_2_si", "dof_si"], inplace=True)

    for element in elements:
        df[f"reduced_chi_2_{element}_si_ratio"] = df[f"chi_2_{element}_si_ratio"] / df[f"dof_{element}_si_ratio"]
        df.drop(columns=[f"chi_2_{element}_si_ratio", f"dof_{element}_si_ratio"], inplace=True)

    df = filter_by_peak_counts(df, si_peak_col, filter_percentage, peak_columns)

    os.makedirs(plot_save_dir, exist_ok=True)


def plot_predictions():
    df = pd.read_csv("/home/sm/Downloads/predictions.csv")
    for element in ["al", "mg", "si", "fe"]:
        plot_prediction_ratio(df, "latitude", "longitude", f"model_{element}_prediction", ".", "turbo", 1.5)


if __name__ == "__main__":
    plot_predictions()
    # process_and_plot(
    #     input_json="/home/sm/Downloads/ISRO.fibnacci_lat_lon.json",
    #     plot_save_dir=".",
    #     si_peak_col="peak_si_c",
    #     peak_columns=["peak_mg_c", "peak_al_c", "peak_ca_c", "peak_ti_c", "peak_fe_c"],
    #     filter_percentage=50,
    #     bins=50,
    #     cmap="viridis",
    # )
