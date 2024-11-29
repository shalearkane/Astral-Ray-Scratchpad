import pandas as pd

# Load the theoretical spectrum from the CSV file
theoretical_spectrum_df = pd.read_csv('total_scattered_spectrum.csv')

# Check the first few rows of the data
print(theoretical_spectrum_df.head())

# Check for missing (NaN) values in the theoretical spectrum
missing_values = theoretical_spectrum_df.isnull().sum()
print("Missing values in each column:", missing_values)

# Interpolate missing values in the "Total Scattered Spectrum" column
theoretical_spectrum_interpolated = theoretical_spectrum_df.copy()
theoretical_spectrum_interpolated['Total Scattered Spectrum'] = theoretical_spectrum_interpolated['Total Scattered Spectrum'].interpolate()


theoretical_spectrum_interpolated.to_csv('theoretical_spectrum_interpolated.csv')