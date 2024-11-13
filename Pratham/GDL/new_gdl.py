import pexpect
import os
import time

def initialize_gdl(log_file):
    """
    Initializes the GDL environment and returns the child process.
    
    :param log_file: Path to the log file.
    :return: The child process running GDL.
    """
    child = pexpect.spawn("tcsh", encoding="utf-8", timeout=60)
    child.logfile = log_file
    child.sendline("sswgdl")
    child.expect("GDL> ")
    child.sendline('o=ospex(/no_gui)')
    child.expect("GDL> ")
    return child

def set_spex_file_reader(child):
    """
    Sets the spex file reader in the GDL session.
    
    :param child: The GDL session child process.
    """
    child.sendline("o->set, spex_file_reader='ch2xsm_read'")
    child.expect("GDL> ")

def set_fit_parameters(child):
    """
    Sets the fit parameters in the GDL session.
    
    :param child: The GDL session child process.
    """
    child.sendline('o->set, fit_function="vth_abun"')
    child.expect("GDL> ")
    child.sendline('o->set, fit_comp_params=[1.00000, 2.00000, 1.00000, 1.00000, 1.00000, 1.00000, 1.00000, 1.00000]')
    child.expect("GDL> ")
    child.sendline('o->set, fit_comp_minima=[1.00000e-20, 0.500000, 0.100000, 0.100000, 0.100000, 0.100000, 0.100000, 0.100000]')
    child.expect("GDL> ")
    child.sendline('o->set, fit_comp_maxima=[1.00000e+20, 8.00000, 2.00000, 2.00000, 2.00000, 2.00000, 2.00000, 2.00000]')
    child.expect("GDL> ")
    child.sendline('o->set, fit_comp_free_mask=[1B, 1B, 1B, 1B, 0B, 0B, 0B, 0B]')
    child.expect("GDL> ")
    child.sendline('o->set, spex_eband=[[1.02800, 1.75763], [1.75763, 3.00513], [3.00513, 5.13806], [5.13806, 8.78485], [8.78485, 15.0200]]')
    child.expect("GDL> ")

def process_file(child, file_path, output_dir):
    """
    Processes a single file and writes the output to a text file.
    
    :param child: The GDL session child process.
    :param file_path: The path to the input file.
    :param output_dir: Directory where output files will be saved.
    :return: The path to the output file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Set the input file in the GDL session
    child.sendline(f'o->set, spex_specfile="{file_path}"')
    child.expect("GDL> ")
    
    # Define the output file path
    output_filename = os.path.splitext(os.path.basename(file_path))[0] + '_output.txt'
    output_filepath = os.path.join(output_dir, output_filename)
    
    # Write the output to the file
    child.sendline(f'o->textfile, spex_units=units, filename="{output_filepath}"')
    child.expect("GDL> ")
    
    return output_filepath

def close_gdl(child):
    """
    Closes the GDL session.
    
    :param child: The GDL session child process.
    """
    child.sendline('exit')
    child.expect('% ')
    child.sendline('exit')
    child.expect(pexpect.EOF)

def automate_ospex(file_list, output_dir, log_file='automation_log.txt'):
    """
    Automates running OSPEX for multiple files using GDL within a tcsh shell.
    
    :param file_list: List of file paths to process.
    :param output_dir: Directory where output files will be saved.
    :param log_file: Path to the log file.
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(log_file, 'w') as log:
        try:
            # Initialize GDL and OSPEX environment
            child = initialize_gdl(log)
            set_spex_file_reader(child)
            child.sendline("o->xinput")
            child.expect("GDL> ")
            
            for file_path in file_list:
                try:
                    output_filepath = process_file(child, file_path, output_dir)
                    log.write(f"Processed file: {file_path} -> Output saved at: {output_filepath}\n")
                    print(f"Processed file: {file_path} -> Output saved at: {output_filepath}")
                    time.sleep(2)  # Optional delay between files
                except FileNotFoundError as e:
                    log.write(str(e) + "\n")
                    print(e)
            
            # Close the GDL environment
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

if __name__ == "__main__":
    files_to_process = [
        "/home/pg/ISRO_Inter_IIT/XSM_files/ch2_xsm_20240711_v1_level2.pha",
        "/home/pg/Downloads/X2ABUND_LMODEL_V1/ch2_xsm_20210827_v1/xsm/data/2021/08/27/calibrated/ch2_xsm_20210827_v1_level2.pha",
        # Add more file paths as needed
    ]
    output_directory = "/home/pg/ISRO_Inter_IIT/XSM_outputs/"
    automate_ospex(files_to_process, output_directory)
