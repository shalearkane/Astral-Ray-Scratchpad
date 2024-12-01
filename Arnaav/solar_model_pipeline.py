import os
import datetime
from pymongo import MongoClient
from helpers.download import download_file_from_file_server
import pexpect
import pandas as pd
from io import TextIOWrapper, StringIO


# Function to download XSM files
def get_xsm_files(start_time: datetime.datetime, end_time: datetime.datetime, output_dir: str):
    
    from constants.mongo import (
        MONGO_URI = "172.20.101.53:27017"
        DATABASE_ISRO = "ISRO"
        COLLECTION_XSM_PRIMARY = "xsm_primary"

    )
    
    class_fits_accepted = MongoClient(MONGO_URI)[DATABASE_ISRO][COLLECTION_XSM_PRIMARY]

    filter = {
        "parsedStartTime": {
            "$gte": start_time,
            "$lte": end_time,
        },
        "ext": "pha",
    }

    project = {"_id": 1, "path": 1}
    result = class_fits_accepted.find(filter=filter, projection=project)
    
    os.makedirs(output_dir, exist_ok=True)
    
    for doc in result:
        download_file_from_file_server(doc, "primary_xsm", output_dir)



def initialize_gdl(log_file: TextIOWrapper):
    child = pexpect.spawn("tcsh", encoding="utf-8", timeout=60)
    child.logfile = log_file
    child.sendline("sswgdl")
    child.sendline("o=ospex(/no_gui)")
    child.sendline("o->set, spex_file_reader='ch2xsm_read'")
    child.sendline('o->set, fit_function="vth_abun"')
    child.sendline("o->set, fit_comp_params=[1.00000, 2.00000, 1.00000, 1.00000, 1.00000, 1.00000, 1.00000, 1.00000]")
    child.sendline("o->set, fit_comp_minima=[1.00000e-20, 0.500000, 0.100000, 0.100000, 0.100000, 0.100000, 0.100000, 0.100000]")
    child.sendline("o->set, fit_comp_maxima=[1.00000e+20, 8.00000, 2.00000, 2.00000, 2.00000, 2.00000, 2.00000, 2.00000]")
    child.sendline("o->set, fit_comp_free_mask=[1B, 1B, 1B, 1B, 0B, 0B, 0B, 0B]")
    child.sendline("o->set, spex_eband=[[1.02800, 1.75763], [1.75763, 3.00513], [3.00513, 5.13806], [5.13806, 8.78485], [8.78485, 15.0200]]")
    return child



def process_file(child, file_path, output_dir):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    
    child.sendline(f'o->set, spex_specfile="{file_path}"')

    
    output_filename = os.path.splitext(os.path.basename(file_path))[0] + "_output.txt"
    output_filepath = os.path.join(output_dir, output_filename)

    
    child.sendline(f'o->textfile, spex_units=units, filename="{output_filepath}"')

     # time.sleep(2)

    # if not os.path.exists(output_filepath):
    #     raise FileNotFoundError(f"Output file not generated: {output_filepath}")

    return output_filepath



def close_gdl(child):
    child.close()



def process_raw_energy_bins(file_list, output_dir, log_file="automation_log.txt"):
    os.makedirs(output_dir, exist_ok=True)
    with open(log_file, "w") as log:
        try:
            
            child = initialize_gdl(log)
            child.sendline("o->xinput")

            for file_path in file_list:
                try:
                    output_filepath = process_file(child, file_path, output_dir)
                    log.write(f"Processed file: {file_path} -> Output saved at: {output_filepath}\n")
                    print(f"Processed file: {file_path} -> Output saved at: {output_filepath}")
                except FileNotFoundError as e:
                    log.write(str(e) + "\n")
                    print(e)

            
            close_gdl(child)
            print("Automation complete. Check the log file for details.")

        except pexpect.EOF:
            log.write("The child process exited unexpectedly.\n")
            print("The child process exited unexpectedly.")
        except pexpect.TIMEOUT:
            log.write("Timeout occurred while waiting for the child process.\n")
            print("Timeout occurred while waiting for the child process.")
        except Exception as e:
            log.write(f"An unexpected error occurred: {e}\n")
            print(f"An unexpected error occurred: {e}")



def get_flux_from_energy_bins(
    input_file_path: str,
    output_file_path: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
):
    format_string = "%d-%b-%Y %H:%M:%S.%f"

    with open(input_file_path, "r") as f_in, open(output_file_path, "w") as f_out:
        lines = f_in.readlines()
        lines = lines[5:]  
        header = lines[0].split("      ")
        header[0] = "time"  

        df = pd.read_csv(StringIO("\n".join(lines[2:])), sep="\s+", header=None)
        df[0] += " " + df[1]
        df = df.drop(df.columns[[1]], axis=1)
        df.columns = header
        df["time"] = df["time"].apply(lambda x: datetime.datetime.strptime(x, format_string))

        filtered_df = df[(df["time"] >= start_time) & (df["time"] <= end_time)]
        sum_df = filtered_df.sum(axis=0, numeric_only=True)

        for idx, value in zip(sum_df.index, sum_df.values):
            low, high = idx.split("-")
            low = float(low)
            high = float(high)
            mid = (high + low) / 2
            f_out.write(f"{mid:.2f} 0.0 {value:.4f}\n")



def main_pipeline(start_time: datetime.datetime, end_time: datetime.datetime):
    
    xsm_output_dir = "data/xsm"
    raw_energy_output_dir = "data/raw_energy"
    flux_output_dir = "data/flux"
    os.makedirs(flux_output_dir, exist_ok=True)

    
    get_xsm_files(start_time, end_time, xsm_output_dir)

    
    pha_files = [os.path.join(xsm_output_dir, f) for f in os.listdir(xsm_output_dir) if f.endswith(".pha")]
    process_raw_energy_bins(pha_files, raw_energy_output_dir)

    
    for raw_file in os.listdir(raw_energy_output_dir):
        if raw_file.endswith("_output.txt"):
            input_file_path = os.path.join(raw_energy_output_dir, raw_file)
            output_file_path = os.path.join(flux_output_dir, f"output_{start_time.strftime('%Y%m%d%H%M')}_{end_time.strftime('%Y%m%d%H%M')}.txt")
            get_flux_from_energy_bins(input_file_path, output_file_path, start_time, end_time)

    print("Pipeline execution complete.")


if __name__ == "__main__":
    
    start_time = datetime.datetime(2024, 8, 27, 0, 0, 0, tzinfo=datetime.timezone.utc)
    end_time = datetime.datetime(2024, 9, 27, 23, 59, 59, tzinfo=datetime.timezone.utc)

    
    main_pipeline(start_time, end_time)
