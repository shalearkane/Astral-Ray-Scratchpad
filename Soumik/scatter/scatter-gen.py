from generate_fits import create_fits_file
from scatter_from_incident import scatter_from_incident


def scatter_gen():
    data_folder_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/model/data_constants"
    incident_solar_file_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Khushi/scattered/model.2.txt"
    scatter_df = scatter_from_incident(data_folder_path, incident_solar_file_path)
    create_fits_file(scatter_df, "some.fits")

if __name__ == "__main__":
    scatter_gen()
