import pandas as pd
import numpy as np
import matplotlib
from typing import List
from pandas import DataFrame

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

input_csv: str = "/home/av/Documents/Visual Shit/combined_data_final.csv"
df: DataFrame = pd.read_csv(input_csv)

def filter_by_peak_counts(df: DataFrame, si_peak_col: str, percentage: float, peak_columns: List[str]) -> DataFrame:
    threshold: float = percentage / 100.0
    for col in peak_columns:
        df = df[df[col] >= df[si_peak_col] * threshold]
    return df

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

si_peak_col: str = "peak_si_c"
peak_columns: List[str] = ["peak_mg_c", "peak_al_c", "peak_ca_c", "peak_ti_c", "peak_fe_c"]
df = filter_by_peak_counts(df, si_peak_col, 50, peak_columns)

output_csv: str = "/home/av/Documents/Visual Shit/preprocessed_data_new.csv"
df.to_csv(output_csv, index=False)

print(f"Preprocessing complete. Updated data saved to {output_csv}.")

def plot_and_save_heatmap(df: DataFrame, x_col: str, y_col: str, save_dir: str, bins: int = 50, cmap: str = "viridis") -> None:
    plt.figure(figsize=(8, 6))
    heatmap, xedges, yedges = np.histogram2d(df[x_col], df[y_col], bins=bins)
    extent: List[float] = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    plt.imshow(heatmap.T, extent=extent, origin='lower', cmap=cmap, aspect='auto') # type: ignore
    plt.colorbar(label="Density")
    plt.title(f"{x_col} vs {y_col} Heatmap", fontsize=14)
    plt.xlabel(x_col, fontsize=12)
    plt.ylabel(y_col, fontsize=12)
    
    file_name: str = f"{x_col}_vs_{y_col}_heatmap.png".replace(" ", "_")
    save_path: str = os.path.join(save_dir, file_name)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Heatmap saved: {save_path}")

plot_save_dir: str = "/home/av/Documents/Visual Shit/plots"
os.makedirs(plot_save_dir, exist_ok=True)

plot_and_save_heatmap(df, "reduced_chi_2_mg_si_ratio", "reduced_chi_2_al_si_ratio", plot_save_dir)
plot_and_save_heatmap(df, "wt_mg_si_ratio", "wt_al_si_ratio", plot_save_dir)
