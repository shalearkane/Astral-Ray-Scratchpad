from astropy.io import fits


import matplotlib.pyplot as plt
import numpy as np


# Replace 'your_file.arf' with the path to your ARF file
arf_file = '/home/pg/Downloads/X2ABUND_LMODEL_V1/ch2_xsm_20240711_0144-0147.arf'

# Open the ARF file
with fits.open(arf_file) as hdul:
    # Print information about the file structure
    hdul.info()

    # Inspect the main data table (usually in the first HDU)
    arf_data = hdul[1].data
    print(arf_data.columns)  # List all columns available in the ARF file

    # Extract specific columns, e.g., ENERG_LO, ENERG_HI, and SPECRESP
    energy_lo = arf_data['ENERG_LO']
    energy_hi = arf_data['ENERG_HI']
    effective_area = arf_data['SPECRESP']

    # Print a sample of the data
    print("Energy Low (keV):", energy_lo[:5])
    print("Energy High (keV):", energy_hi[:5])
    print("Effective Area (cm^2):", effective_area[:5])

    import pandas as pd
energy=(energy_hi + energy_lo)/2

# Assuming 'energy' and 'effective_area' are defined lists or arrays
area_kev = pd.DataFrame({
    "Kev": energy,
    "Area": effective_area
})

# Display the DataFrame
print(area_kev)



# Calculate the center of each energy bin
energy = (energy_lo + energy_hi) / 2

# Plot effective area as a function of energy
plt.plot(energy, effective_area, label='Effective Area')
plt.xlabel("Energy (keV)")
plt.ylabel("Effective Area (cm²)")
plt.title("Instrument Effective Area (ARF)")
plt.legend()
plt.show()


from astropy.io import fits
from astropy.table import Table

# set memmap=True for large files
hdu_list =  fits.open("/home/pg/Downloads/X2ABUND_LMODEL_V1/ch2_xsm_20240711_0144-0147.pha", memmap=True)
print(hdu_list.info())
    # select the HDU you want
hdu = hdu_list[1].data
    # read into an astropy Table object

table = Table(hdu)

table.write('/home/pg/ISRO_Inter_IIT/channels_counts_20240711.csv', delimiter=',',  overwrite=True)

file_path = '/home/pg/ISRO_Inter_IIT/channels_counts_20240711.csv'

# or
df = pd.read_csv(file_path)  

# Replace 'Column1' and 'Column2' with the actual column names you want to plot


df['Kev']=(df['CHANNEL']*33+500)/1000

df['counts_kev']=df['COUNTS']/df['Kev']

x = df['Kev']
y = df['counts_kev']

# Line plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, marker='o', linestyle='-')
plt.xlabel('Kev')
plt.ylabel('counts')
plt.title('Line Plot')
plt.show()



# Define a tolerance value for matching the ranges (adjust if needed)
tolerance = 0.05  # Adjust this based on your data distribution

# Create a new column in df to store the averaged 'Area' values
df['Avg_Area'] = np.nan


for i, kev_value in enumerate(df['Kev']):
    # Find values in area_kev['Kev'] that are within the tolerance range of kev_value
    matching_areas = area_kev[(area_kev['Kev'] >= kev_value - tolerance) & (area_kev['Kev'] <= kev_value + tolerance)]
    
    # Calculate the average area for these matched values
    avg_area = matching_areas['Area'].mean() if not matching_areas.empty else np.nan
    
    # Assign the computed average to the new column in df
    df.at[i, 'Avg_Area'] = avg_area


df['counts_kev_area']=df['counts_kev']/df['Avg_Area']

x = df['Kev']
y = df['counts_kev_area']

# Line plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, marker='o', linestyle='-')
plt.xlabel('keV')
plt.ylabel('counts per second Kev')
plt.title('Line Plot')
plt.show()