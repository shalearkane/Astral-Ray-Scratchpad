import os
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

from preprocess import preprocess_and_remove_duplicates

selected_elements = ["fe", "ti", "ca", "si", "al", "mg", "na", "o"]
atomic_masses = {
    "fe": 56,
    "ti": 48,
    "ca": 40,
    "si": 28,
    "al": 27,
    "mg": 24.3,
    "na": 23,
    "o": 16,
}

atomic_number_map = {
    "fe": 26,
    "ti": 22,
    "ca": 20,
    "si": 14,
    "al": 13,
    "mg": 12,
    "na": 11,
    "o": 8,
}

element_properties = {
    "fe": {"abundance": 3.71879, "density": 7.8600},
    "ti": {"abundance": 1.09157e-06, "density": 4.5},
    "ca": {"abundance": 16.5994, "density": 1.5500},
    "si": {"abundance": 15.1719, "density": 2.3200},
    "al": {"abundance": 17.0742, "density": 2.6941},
    "mg": {"abundance": 2.26579, "density": 1.7350},
    "na": {"abundance": 6.77069e-06, "density": 0.9690},
    "o": {"abundance": 45.0000, "density": 1.3310e-03},
}


def load_ffast_data(file_path: str):
    try:
        data = pd.read_csv(file_path, sep="\\s+", comment="#", header=None)
        data = data[pd.to_numeric(data[0], errors="coerce").notnull()]
        data.reset_index(drop=True, inplace=True)
        num_columns = data.shape[1]

        if num_columns == 14:
            data.columns = [
                "Energy",
                "F1",
                "F2",
                "MuRho",
                "SigmaRho",
                "Column6",
                "Column7",
                "Column8",
                "Column9",
                "Column10",
                "Column11",
                "Column12",
                "Column13",
                "Column14",
            ]
        elif num_columns == 13:
            data.columns = [
                "Energy",
                "F1",
                "F2",
                "MuRho",
                "SigmaRho",
                "Column6",
                "Column7",
                "Column8",
                "Column9",
                "Column10",
                "Column11",
                "Column12",
                "Column13",
            ]
        else:
            return None

        data = data[["Energy", "F1", "F2", "MuRho", "SigmaRho"]].dropna()
        data = data.apply(pd.to_numeric, errors="coerce")

        return data
    except Exception as e:
        return None


def interpolate_cross_section(data, energies):
    interpolation_function = interp1d(data["Energy"], data["SigmaRho"], kind="linear", fill_value="extrapolate")  # type: ignore
    return interpolation_function(energies)


def model_scattered_spectrum_with_density(ffast_data_dict: dict, incident_spectrum, energies):
    total_scattered_spectrum = np.zeros_like(incident_spectrum)
    for element, properties in element_properties.items():
        abundance = properties["abundance"]
        density = properties["density"]

        if element in ffast_data_dict:
            element_data = ffast_data_dict[element]
            sigma_rho_interpolated = interpolate_cross_section(element_data, energies)
            atomic_mass = atomic_masses.get(element, 1)
            number_density = abundance * density / atomic_mass
            element_scattered_spectrum = number_density * sigma_rho_interpolated * incident_spectrum
            total_scattered_spectrum += element_scattered_spectrum
        else:
            continue

    return total_scattered_spectrum


def load_incident_spectrum(file_path: str) -> pd.DataFrame:
    incident_data = pd.read_csv(file_path, sep="\\s+", header=None)
    incident_data.columns = ["Energy", "Column2", "Intensity"]
    incident_data = incident_data.drop(columns=["Column2"])
    incident_data = incident_data.apply(pd.to_numeric, errors="coerce")
    return incident_data[["Energy", "Intensity"]]


def scatter_from_incident(data_folder_path: str, incident_solar_file_path: str) -> pd.DataFrame:
    ffast_folder_path = os.path.join(data_folder_path, "ffast")
    ffast_data_dict = {}

    for element in selected_elements:

        atomic_number = atomic_number_map[element]
        file_name = f"ffast_{atomic_number}_{element}.txt"
        file_path = os.path.join(ffast_folder_path, file_name)

        if os.path.exists(file_path):
            data = load_ffast_data(file_path)
            if data is not None:
                ffast_data_dict[element] = data

    incident_spectrum = load_incident_spectrum(incident_solar_file_path)

    energies = incident_spectrum["Energy"].values
    incident_intensity = incident_spectrum["Intensity"].values

    total_scattered_spectrum = model_scattered_spectrum_with_density(ffast_data_dict, incident_intensity, energies)

    result_df = pd.DataFrame({"keV": energies, "scattered_spectrum": total_scattered_spectrum})
    result_df = preprocess_and_remove_duplicates(result_df, "keV")

    return result_df


if __name__ == "__main__":
    data_folder_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/model/data_constants"
    incident_solar_file_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Khushi/scattered/model.2.txt"
    output_file_path = "total_scattered_spectrum.csv"

    result_df = scatter_from_incident(data_folder_path, incident_solar_file_path)
    result_df.to_csv(output_file_path, index=False)
