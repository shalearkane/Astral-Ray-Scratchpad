import os
import datetime
from helpers.download import download_file_from_file_server
from helpers.query_xsm import get_xsm_pha
from GDL.raw_energy_bins import automate_ospex
from GDL.flux_from_raw_energy_bins import get_flux_from_energy_bins



# Function to download XSM files
def get_xsm_files(start_time: datetime.datetime, end_time: datetime.datetime, output_dir: str) -> dict:
    docs = get_xsm_pha(start_time, end_time)
    os.makedirs(output_dir, exist_ok=True)

    for doc in docs:
        download_file_from_file_server(doc, "primary_xsm", output_dir)

    return doc


# Main pipeline function
def main_pipeline(start_time: datetime.datetime, end_time: datetime.datetime):

    xsm_output_dir = "data/xsm"
    raw_energy_output_dir = "data/raw_energy"
    flux_output_dir = "data/flux"
    os.makedirs(flux_output_dir, exist_ok=True)


    get_xsm_files(start_time, end_time, xsm_output_dir)


    pha_files = [os.path.join(xsm_output_dir, f) for f in os.listdir(xsm_output_dir) if f.endswith(".pha")]
    automate_ospex(pha_files, raw_energy_output_dir)


    for raw_file in os.listdir(raw_energy_output_dir):
        if raw_file.endswith("_output.txt"):
            input_file_path = os.path.join(raw_energy_output_dir, raw_file)
            output_file_path = os.path.join(flux_output_dir, f"output_{start_time.strftime('%Y%m%d%H%M')}_{end_time.strftime('%Y%m%d%H%M')}.txt")
            final_df=get_flux_from_energy_bins(input_file_path, output_file_path, start_time, end_time)

    print(final_df)
    print("Pipeline execution complete.")



if __name__ == "__main__":

    start_time = datetime.datetime(2024, 8, 27, 0, 0, 0, tzinfo=datetime.timezone.utc)
    end_time = datetime.datetime(2024, 9, 27, 23, 59, 59, tzinfo=datetime.timezone.utc)


    main_pipeline(start_time, end_time)
