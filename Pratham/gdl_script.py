import pexpect
import sys
import time
import os

def automate_ospex(file_list, output_dir, log_file='automation_log.txt'):
    """
    Automates running OSPEX for multiple files using GDL within a tcsh shell.

    :param file_list: List of file paths to process.
    :param output_dir: Directory where output files will be saved.
    :param log_file: Path to the log file.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Open the log file
        with open(log_file, 'w') as log:
            # Start the tcsh shell
            child = pexpect.spawn("tcsh", encoding="utf-8", timeout=60)
            child.logfile = log

            # Start sswgdl
            child.sendline("sswgdl")

            # Wait for the GDL prompt
            child.expect("GDL> ")

            # Initialize OSPEX without GUI
            child.sendline('o=ospex(/no_gui)')
            child.expect("GDL> ")

            # Set spex_file_reader
            child.sendline("o->set, spex_file_reader='ch2xsm_read'")
            child.expect("GDL> ")

            # Initialize input
            child.sendline("o->xinput")
            child.expect("GDL> ")

            for file_path in file_list:
                # Check if the file exists
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    log.write(f"File not found: {file_path}\n")
                    continue

                # Set the spex_specfile
                child.sendline(f'o->set, spex_specfile="{file_path}"')
                child.expect("GDL> ")

                # Set fit_function
                child.sendline('o->set, fit_function="vth_abun"')
                child.expect("GDL> ")

                # Set fit_comp_params
                child.sendline('o->set, fit_comp_params=[1.00000, 2.00000, 1.00000, 1.00000, 1.00000, 1.00000, 1.00000, 1.00000]')
                child.expect("GDL> ")

                # Set fit_comp_minima
                child.sendline('o->set, fit_comp_minima=[1.00000e-20, 0.500000, 0.100000, 0.100000, 0.100000, 0.100000, 0.100000, 0.100000]')
                child.expect("GDL> ")

                # Set fit_comp_maxima
                child.sendline('o->set, fit_comp_maxima=[1.00000e+20, 8.00000, 2.00000, 2.00000, 2.00000, 2.00000, 2.00000, 2.00000]')
                child.expect("GDL> ")

                # Set fit_comp_free_mask
                child.sendline('o->set, fit_comp_free_mask=[1B, 1B, 1B, 1B, 0B, 0B, 0B, 0B]')
                child.expect("GDL> ")

                # Set spex_eband
                child.sendline('o->set, spex_eband=[[1.02800, 1.75763], [1.75763, 3.00513], [3.00513, 5.13806], [5.13806, 8.78485], [8.78485, 15.0200]]')
                child.expect("GDL> ")

                # Set output textfile
                output_filename = os.path.splitext(os.path.basename(file_path))[0] + '_output.txt'
                output_filepath = os.path.join(output_dir, output_filename)
                child.sendline(f'o->textfile, spex_units=units, filename="{output_filepath}"')
                child.expect("GDL> ")

                # Run the OSPEX script or perform the fit
                # Assuming you have an OSPEX procedure to run the fit
                # Example:
                # child.sendline('.run /path/to/your_ospex_script.pro')
                # child.expect("GDL> ")

                print(f"Processed file: {file_path} -> Output saved at: {output_filepath}")
                log.write(f"Processed file: {file_path} -> Output saved at: {output_filepath}\n")

                # Optional: Add a short delay between files
                time.sleep(2)

            # Exit the GDL interactive environment
            child.sendline('exit')
            child.expect('% ')

            # Exit tcsh
            child.sendline('exit')
            child.expect(pexpect.EOF)

            print("Automation complete. Check the log file for details.")

    except pexpect.EOF:
        print("The child process exited unexpectedly.")
    except pexpect.TIMEOUT:
        print("Timeout occurred while waiting for the child process.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Define the list of files to process
    files_to_process = [
        "/home/pg/ISRO_Inter_IIT/XSM_files/ch2_xsm_20240711_v1_level2.pha",
        "/home/pg/Downloads/X2ABUND_LMODEL_V1/ch2_xsm_20210827_v1/xsm/data/2021/08/27/calibrated/ch2_xsm_20210827_v1_level2.pha",
        # Add more file paths as needed
    ]

    # Define the output directory
    output_directory = "/home/pg/ISRO_Inter_IIT/XSM_outputs/"

    automate_ospex(files_to_process, output_directory)
