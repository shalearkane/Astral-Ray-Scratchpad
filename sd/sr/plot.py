import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
#from gall_peters import gal_peters,inverse_gal_peters

# Function to visualize the data
def visualize_data(df: pd.DataFrame, elem_wt: str):
    # Set up the colormap normalization and color mapping
    #norm = Normalize(vmin=0, vmax=5)
    cmap = plt.cm.viridis

    # Create polygons and associate data for coloring
    patches = []
    colors = []
    for _, row in df.iterrows():
        #if row[elem_wt] < 5 and row[elem_wt] > 0:
        polygon = [
            (row["V0_LONGITUDE"], row["V0_LATITUDE"]),
            (row["V3_LONGITUDE"], row["V3_LATITUDE"]),
            (row["V2_LONGITUDE"], row["V2_LATITUDE"]),
            (row["V1_LONGITUDE"], row["V1_LATITUDE"]),
        ]
        patches.append(Polygon(polygon, closed=True))
        colors.append(row[elem_wt])

    # Plot polygons
    fig, ax = plt.subplots(figsize=(10, 10))
    patch_collection = PatchCollection(patches, cmap=cmap)# norm=norm)
    patch_collection.set_array(colors)
    ax.add_collection(patch_collection)

    # Add colorbar
    # cbar = plt.colorbar(patch_collection, ax=ax)
    # cbar.set_label(f"{elem_wt} (weight percentage)")
    #cbar.set_ticks([0, 1, 2, 3, 4, 5])
    #cbar.ax.set_yticklabels(['0', '1', '2', '3', '4', '5'])

    # Set axis labels and limits
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_xlim(df[["V0_LONGITUDE", "V1_LONGITUDE", "V2_LONGITUDE", "V3_LONGITUDE"]].min().min(),
                df[["V0_LONGITUDE", "V1_LONGITUDE", "V2_LONGITUDE", "V3_LONGITUDE"]].max().max())
    ax.set_ylim(df[["V0_LATITUDE", "V1_LATITUDE", "V2_LATITUDE", "V3_LATITUDE"]].min().min(),
                df[["V0_LATITUDE", "V1_LATITUDE", "V2_LATITUDE", "V3_LATITUDE"]].max().max())

    # Remove x-axis, y-axis, labels, and legends
    plt.axis('off')  # Turns off both axes
    plt.gca().set_frame_on(False)  # Optional: Removes the border frame
    plt.gca().legend_ = None


    # plt.yticks(np.linspace(30,50,50))
    # Save and show the plot
    # plt.savefig(f"./plottings/{elem_wt}_o_changed2.png", bbox_inches="tight", dpi=300)
    plt.savefig(f"./plottings/{elem_wt}_o_changed2.png", bbox_inches="tight", dpi=600, pad_inches=0,  transparent=True)

    #plt.show()

# Load data and visualize





data = pd.read_csv("output.csv")
data.columns = data.columns.str.strip()
for elem_wt in [ "MG_WT","SI_WT","FE_WT","AL_WT"]:
    # Call the function with the relevant columns
    print(data["MG_WT"])
    visualize_data(
        data[
            [
                "V0_LATITUDE",

                "V0_LONGITUDE",
                "V1_LATITUDE",
                "V1_LONGITUDE",
                "V2_LATITUDE",
                "V2_LONGITUDE",
                "V3_LATITUDE",
                "V3_LONGITUDE",
                elem_wt,
            ]
        ],
        elem_wt,
    )
