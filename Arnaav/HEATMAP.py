import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

# Load JSON data
json_file = "/home/av/Documents/ISRO.test.json"  # Replace with your JSON file path
with open(json_file, "r") as file:
    data = json.load(file)

# Extract relevant fields
records = []
for entry in data:
    if "lat" in entry and "lon" in entry and "wt" in entry:
        lat = entry["lat"]
        lon = entry["lon"]
        weights = entry["wt"]  # Dictionary of element weights
        # Append each element and its weight to the list
        for element, weight in weights.items():
            records.append({"lat": lat, "lon": lon, "element": element, "weight": weight})

# Create a DataFrame
df = pd.DataFrame(records)

# Output directory for heatmaps
output_dir = "home/av/Documents/heatmaps"  # Directory to save the heatmaps
os.makedirs(output_dir, exist_ok=True)

# Unique elements in the data
elements = df["element"].unique()

# Generate heatmaps for each element
for element in elements:
    df_element = df[df["element"] == element]

    # Generate heatmap data
    latitudes = np.sort(df_element["lat"].unique())
    longitudes = np.sort(df_element["lon"].unique())
    print(longitudes)
    grid = df_element.pivot(index="lat", columns="lon", values="weight")

    # Plot the heatmap
    plt.figure(figsize=(12, 8))
    plt.pcolormesh(
        grid.columns,  # Longitude
        grid.index,  # Latitude
        grid.values,  # Weight values
        cmap="viridis",  # Color map
        shading="auto"  # Smooth grid
    )
    plt.colorbar(label=f"{element.capitalize()} Weight (%)")
    plt.title(f"Heatmap of {element.capitalize()} Weight", fontsize=16)
    plt.xlabel("Longitude", fontsize=14)
    plt.ylabel("Latitude", fontsize=14)
    plt.tight_layout()

    # Save the heatmap
    output_file = os.path.join(output_dir, f"{element}_heatmap.png")
    plt.savefig(output_file)
    plt.close()

    print(f"Heatmap for element '{element}' saved as {output_file}")

print("All heatmaps generated and saved.")
