import pandas as pd
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt

# Load your CSV data
data = pd.read_csv("/home/pg/Documents/Astral-Ray-Scratchpad/Pratham/1-s2.0-S0019103523004773-mmc3.csv")

# Strip leading and trailing spaces from the column names
data.columns = data.columns.str.strip()

# Define the grid resolution (0.41° by 0.41°)
pixel_size = 0.41

# Define grid dimensions (latitude: -90 to 90, longitude: -180 to 180)
latitudes = np.arange(-90, 90, pixel_size)
longitudes = np.arange(-180, 180, pixel_size)

# Initialize an empty grid to store the values (use NaN for areas without data)
grid = np.full((len(latitudes), len(longitudes)), np.nan)

# Function to map coordinates to the grid and assign values
def assign_value_to_grid(row):
    # Get the min/max latitudes and longitudes
    lat_min = min(row['V0_LATITUDE'], row['V1_LATITUDE'], row['V2_LATITUDE'], row['V3_LATITUDE'])
    lat_max = max(row['V0_LATITUDE'], row['V1_LATITUDE'], row['V2_LATITUDE'], row['V3_LATITUDE'])
    lon_min = min(row['V0_LONGITUDE'], row['V1_LONGITUDE'], row['V2_LONGITUDE'], row['V3_LONGITUDE'])
    lon_max = max(row['V0_LONGITUDE'], row['V1_LONGITUDE'], row['V2_LONGITUDE'], row['V3_LONGITUDE'])

    # Determine the grid cell indices based on coordinates
    lat_idx_min = int((lat_min + 90) // pixel_size)
    lat_idx_max = int((lat_max + 90) // pixel_size)
    lon_idx_min = int((lon_min + 180) // pixel_size)
    lon_idx_max = int((lon_max + 180) // pixel_size)

    # Assign the MG_WT value to the grid cells within the bounding box of the polygon
    value = row['MG_WT']

    # Update the grid with the value
    for lat_idx in range(lat_idx_min, lat_idx_max + 1):
        for lon_idx in range(lon_idx_min, lon_idx_max + 1):
            grid[lat_idx, lon_idx] = value

# Apply the function to each row of the DataFrame
data.apply(assign_value_to_grid, axis=1)

# Normalize the grid values to be in the range 0-255 for image creation
grid_normalized = np.nan_to_num(grid, nan=0)  # Replace NaN with 0 for empty pixels

# Example data: Replace this with your actual grid data
data = grid_normalized.copy()

# Define bicubic interpolation function
def bicubic_interpolate(x, y, data):
    x_coords = np.arange(data.shape[1])
    y_coords = np.arange(data.shape[0])
    interpolator = RegularGridInterpolator((y_coords, x_coords), data, method='cubic')
    return interpolator((y, x))  # (y, x) corresponds to (row, column)

# Parallelize interpolation using ProcessPoolExecutor
def interpolate_grid(new_x, new_y, data):
    interpolated_data = np.zeros((1000, 1000))
    with ProcessPoolExecutor() as executor:
        futures = []
        for i in range(1000):
            print(i)
            for j in range(1000):
                futures.append(executor.submit(bicubic_interpolate, new_x[i], new_y[j], data))
        
        # Collect results
        for k, future in enumerate(futures):
            i = k // 1000
            j = k % 1000
            interpolated_data[i, j] = future.result()
    
    return interpolated_data

# Create new x and y grids for interpolation
new_x = np.linspace(0, data.shape[1] - 1, 1000)
new_y = np.linspace(0, data.shape[0] - 1, 1000)

# Perform parallel interpolation
interpolated_data = interpolate_grid(new_x, new_y, data)

# You can save the result to a file (e.g., npy format, or image if needed)
np.save('interpolated_data.npy', interpolated_data)

# Optionally, create a plot
plt.imshow(interpolated_data, cmap='viridis')
plt.colorbar()
plt.show()
