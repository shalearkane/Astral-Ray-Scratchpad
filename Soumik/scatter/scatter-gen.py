from generate_fits import create_fits_file
from scatter_from_incident import scatter_from_incident
from scatter_from_incident_alt import scatter_from_incident_alt


def scatter_gen():
    data_folder_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/model/data_constants"
    incident_solar_file_path = "/home/sm/Public/Inter-IIT/Astral-Ray-Scratchpad/Soumik/data-generated/flux/flares_flux202206270000_202212272359.txt"
    scatter_df = scatter_from_incident(data_folder_path, incident_solar_file_path)
    create_fits_file(scatter_df, "some.fits")

    scatter_df = scatter_from_incident_alt(incident_solar_file_path)
    create_fits_file(scatter_df, "some-alt.fits")


if __name__ == "__main__":
    scatter_gen()
