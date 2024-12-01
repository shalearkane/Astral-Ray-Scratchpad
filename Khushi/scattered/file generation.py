import os
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from pandas import DataFrame
from astropy.io import fits
from astropy.table import Table
from scatter import *
from fix import *
from generate import *
from constants import *

incident_solarfile_path = "/Users/apple/Desktop/inter iit astro/model.2.txt"
incident_spectrum = load_incident_spectrum(incident_solarfile_path)
folder_path = "/Users/apple/Desktop/inter iit astro/X2ABUND_LMODEL_V1/data_constants/ffast"
ffast_data_dict = {}

for element in selected_elements:
    atomic_number = atomic_number_map[element]
    file_name = f"ffast_{atomic_number}_{element}.txt"
    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path):
        data = pd.read_csv(file_path, sep="\\s+", comment="#", header=None)
        
if incident_spectrum is not None:
    energies = incident_spectrum["Energy"].values
    incident_intensity = incident_spectrum["Intensity"].values

    # Compute total scattered spectrum
    total_scattered_spectrum = model_scattered_spectrum_with_density(
        ffast_data_dict, incident_intensity, energies, element_properties
    )

  
    # Load theoretical spectrum
    theoretical_spectrum_df = pd.read_csv('/Users/apple/Desktop/inter iit astro/total_scattered_spectrum.csv')
    # Interpolate missing values in the "Total Scattered Spectrum" column
    theoretical_spectrum_df['Total Scattered Spectrum'] = theoretical_spectrum_df['Total Scattered Spectrum'].interpolate()

    # Validate shapes and create the final DataFrame
    if len(energies) == len(theoretical_spectrum_df['Total Scattered Spectrum']):
        result_df = pd.DataFrame({
                "Energy": energies,
                "Total Scattered Spectrum": theoretical_spectrum_df['Total Scattered Spectrum']
            })

    # Save to CSV
    output_file_path = "/Users/apple/Desktop/inter iit astro/theoretical_spectrum_interpolated.csv"
    result_df.to_csv(output_file_path, index=False)

# Load and process solar model
solar_model = pd.read_csv(incident_solarfile_path, sep="\\s+", names=["energy", "error", "flux"])
solar_model = preprocess_and_remove_duplicates(solar_model, "energy")
solar_model.to_csv("/Users/apple/Desktop/inter iit astro/model.2.processed.txt", sep=" ", index=False, header=False)

# Load, process, and save theoretical spectrum
theoretical_spectrum_df = pd.read_csv(output_file_path)
processed_theoretical_spectrum = preprocess_and_remove_duplicates(solar_model, "energy")
output_file = "/Users/apple/Desktop/inter iit astro/theoretical_spectrum_processed.csv"
processed_theoretical_spectrum.to_csv(output_file, index=False)

# Convert processed CSV to FITS file
output_fits_file = "/Users/apple/Desktop/inter iit astro/b.fits"
create_fits_file(output_file, output_fits_file)

