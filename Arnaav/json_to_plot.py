import json
import pandas as pd
import numpy as np
import matplotlib
from matplotlib.colors import LogNorm
from typing import List, Optional
from pandas import DataFrame
import os
import matplotlib.pyplot as plt

matplotlib.use('Agg')


def json_to_csv(
    json_file_path: str,
    output_csv_path: str,
    elements: List[str] = None
) -> None:
    if elements is None:
        elements = ["na", "mg", "al", "si", "ca", "ti", "fe"]

    with open(json_file_path, 'r') as file:
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
    df.to_csv(output_csv_path, index=False)
    print(f"Data successfully converted and saved to {output_csv_path}.")


def process_and_plot(
    input_csv: str,
    output_csv: str,
    plot_save_dir: str,
    si_peak_col: str = "peak_si_c",
    al_peak_col: str = "peak_al_c",
    filter_percentage: float = 50,
    cmap: str = "viridis",
    lat_col: str = "latitude",
    lon_col: str = "longitude",
) -> None:
    def filter_by_peak_counts(df: DataFrame, si_peak_col: str, percentage: float, al_peak_col: str) -> DataFrame:
        threshold: float = percentage / 100.0
        df = df[df[al_peak_col] >= df[si_peak_col] * threshold]
        return df

    def plot_feature_scatter(
        df: DataFrame,
        feature_col: str,
        lat_col: str,
        lon_col: str,
        save_dir: str,
        cmap: str = "viridis",
        value_range: Optional[tuple] = None,
        point_size: int = 50,
    ) -> None:
        plt.figure(figsize=(12, 8))
        if value_range:
            df[feature_col] = df[feature_col].clip(lower=value_range[0], upper=value_range[1])
        scatter = plt.scatter(
            df[lon_col],
            df[lat_col],
            c=df[feature_col],
            s=point_size,
            cmap=cmap,
            edgecolors="none",
            alpha=0.8,
            marker='s',
            norm=LogNorm(vmin=value_range[0], vmax=value_range[1]) if value_range else None,
        )
        plt.colorbar(scatter, label=f"Log {feature_col}")
        title = f"Scatter Plot of {feature_col.replace('_', ' ').title()} (Log Gradient)"
        plt.title(title, fontsize=16)
        plt.xlabel("Longitude", fontsize=14)
        plt.ylabel("Latitude", fontsize=14)
        plt.tight_layout()
        file_name = f"{feature_col}_scatter_plot_log.png".replace(" ", "_")
        save_path = os.path.join(save_dir, file_name)
        plt.savefig(save_path, dpi=300)
        plt.close()

    df: DataFrame = pd.read_csv(input_csv)

    elements: List[str] = ["ca", "mg", "al", "ti", "fe"]
    for element in elements:
        df[f"wt_{element}_si_ratio"] = df[f"wt_{element}"] / df["wt_si"]
        df.drop(columns=[f"wt_{element}"], inplace=True)

    df.drop(columns=["wt_si"], inplace=True)

    for element in elements:
        df[f"chi_2_{element}_si_ratio"] = df[[f"chi_2_{element}", "chi_2_si"]].max(axis=1)
        df[f"dof_{element}_si_ratio"] = df[[f"dof_{element}", "dof_si"]].min(axis=1)
        df[f"reduced_chi_2_{element}_si_ratio"] = df[f"chi_2_{element}_si_ratio"] / df[f"dof_{element}_si_ratio"]

    df["reduced_chi_2_si"] = df["chi_2_si"] / df["dof_si"]

    df = filter_by_peak_counts(df, si_peak_col=si_peak_col, percentage=filter_percentage, al_peak_col=al_peak_col)

    df.to_csv(output_csv, index=False)

    os.makedirs(plot_save_dir, exist_ok=True)
    plot_feature_scatter(
        df=df, 
        feature_col="wt_mg_si_ratio", 
        lat_col=lat_col, 
        lon_col=lon_col, 
        save_dir=plot_save_dir, 
        cmap=cmap,
        value_range=(1e-1, 300),
        point_size=.3
    )
    plot_feature_scatter(
        df=df, 
        feature_col="wt_al_si_ratio", 
        lat_col=lat_col, 
        lon_col=lon_col, 
        save_dir=plot_save_dir, 
        cmap=cmap,
        value_range=(1e-1, 300),
        point_size=.3
    )
    plot_feature_scatter(
        df=df, 
        feature_col="reduced_chi_2_si", 
        lat_col=lat_col, 
        lon_col=lon_col, 
        save_dir=plot_save_dir, 
        cmap=cmap,
        value_range=(1e-1, 300),
        point_size=.3
    )


json_file_path = "/home/av/Downloads/ISRO.fibnacci_lat_lon.json"
csv_output_path = "/home/av/Documents/Visual Shit/combined_data_final.csv"
preprocessed_csv_output_path = "/home/av/Documents/Visual Shit/preprocessed_data_new.csv"
plot_save_dir = "/home/av/Documents/Visual Shit/plots"

json_to_csv(json_file_path=json_file_path, output_csv_path=csv_output_path)

process_and_plot(
    input_csv=csv_output_path,
    output_csv=preprocessed_csv_output_path,
    plot_save_dir=plot_save_dir,
    si_peak_col="peak_si_c",
    al_peak_col="peak_al_c",
    filter_percentage=30,
    cmap="viridis",
    lat_col="latitude",
    lon_col="longitude",
)
