Scatter Spectrum Calculation and Data Processing

Table of Contents

  1. Overview
     
  2.File Input and Output
  
  3.Parameters
  
  4.How to Use

  

Overview

This project processes FFAST data, performs interpolation, and calculates the total scattered spectrum for selected elements. It takes as input cross-sectional data files and an incident spectrum, processes them, and outputs the resulting scattered spectrum. The output can be used for further analysis or visualized via plots.


File Input and Output
Input Files

FAST Data Files: These files contain cross-sectional data for each element, and they should be named according to the atomic number and element name (e.g., ffast_12_mg.txt for Magnesium). The data file    should be in a space-separated format and contain the following columns:
        Energy: Energy values in eV (or other units)
        F1, F2, MuRho, SigmaRho: Cross-section data

Incident Spectrum File: The file that contains the incident spectrum data (energy and intensity) for the model. This file should be in a space-separated format with the following columns:
        Energy: Energy values (same unit as FFAST data)
        Intensity: Intensity of the incident spectrum at each energy level

Output Files

  Total Scattered Spectrum: This is the primary output of the code. It is a CSV file containing the energy values and the corresponding total scattered spectrum calculated by the model.
        Energy: Energy values (same as input)
        Total Scattered Spectrum: The computed scattered intensity at each energy level

  Interpolated Spectrum: If any missing values are found in the Total Scattered Spectrum, they are interpolated and saved in a new CSV file. This ensures a smooth spectrum without gaps


Code Structure
Main Script

  Loading FFAST Data (load_ffast_data): This function loads the cross-section data for the selected elements, cleans the data, and formats it for further processing.

  Interpolating SigmaRho (interpolate_cross_section): This function performs linear interpolation on the SigmaRho values based on the energies from the incident spectrum.

  Calculating Scattered Spectrum (model_scattered_spectrum_with_density): This function calculates the total scattered spectrum for each element by considering its density, abundance, and SigmaRho values.

  Loading Incident Spectrum (load_incident_spectrum): This function loads the incident spectrum data (energy and intensity) from the file.

  Main Function (main): This function coordinates the loading of data files, calculation of the scattered spectrum, and saving of the results to a CSV file. It also handles plotting the spectrum.


  Parameters
   1.Element Properties:
     The element_properties dictionary contains the abundance and density for each element. These values are used to calculate the number density and contribute to the scattered spectrum.

   2. Atomic Masses:
     A dictionary of atomic masses is used to convert density and abundance into number density for each element.

  3. FFAST Data Files:
     The names of the FFAST data files should be constructed based on the atomic number and element name (e.g., ffast_12_mg.txt). These files are expected to contain columns for energy and cross-section data.



  How to Use
Step 1: Prepare Input Files

  Ensure you have the correct FFAST data files for the elements you want to process.
  Prepare the incident spectrum file containing energy and intensity values.

Step 2: Update File Paths in the Code

Update the file paths in the code where necessary:

  The path to the folder containing the FFAST data files (folder_path).
  The path to the incident spectrum file (incident_file_path).
  The output file path for saving the scattered spectrum (output_file_path).

Step 3: Run the Script


 
