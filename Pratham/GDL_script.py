import pexpect
import sys
import time

import pexpect
 
# print(pexpect.run('echo hello'))


def automate_ospex():
    try:

        # Start the tcsh shell
        child = pexpect.spawn('tcsh', encoding='utf-8', timeout=None)

        # Optional: Log the session to stdout for debugging
        child.logfile = sys.stdout

        # Wait for the tcsh prompt (adjust if your prompt is different)
        # child.expect('% ')

        # Send 'sswgdl' command
        child.sendline('sswgdl')

        child.logfile = sys.stdout
        # Wait for the GDL prompt (adjust if your prompt is different)
        child.expect('GDL> ')

        # Send 'o=ospex()' command
        child.sendline('o=ospex()')

        # child.sendline('o=ospex(/no_gui)')

        # Wait for the GDL prompt again
        child.expect('GDL> ')

        child.sendline("o->set, spex_file_reader='ch2xsm_read'")

        child.expect('GDL> ')



        
        child.sendline('o->xinput')
        # child.expect('GDL> ')

        # child.sendline('o->set, spex_file_reader="xxx"')
        # child.expect('GDL> ')
        # child.sendline('o->xinput')
        child.expect('GDL> ')

        child.sendline('o->set, spex_specfile="/home/pg/Downloads/X2ABUND_LMODEL_V1/ch2_xsm_20210827_v1/xsm/data/2021/08/27/calibrated/ch2_xsm_20210827_v1_level2.pha"')

        # child.expect('GDL> ')

        # child.sendline('.run /home/pg/ISRO_Inter_IIT/Code/ospex_script_11_nov_2024.pro')


        # child.sendline('o->set, spex_specfile="/home/pg/ISRO_Inter_IIT/XSM_files/ch2_xsm_20240711_v1_level2.pha"')

        child.expect('GDL> ')

        child.sendline('o-> set, fit_function= "vth_abun"')

        child.expect('GDL> ')
        child.sendline('o-> set, fit_comp_params= [1.00000, 2.00000, 1.00000, 1.00000, 1.00000, 1.00000, 1.00000, 1.00000]')

        
        child.expect('GDL> ')

        child.sendline('o-> set, fit_comp_minima= [1.00000e-20, 0.500000, 0.100000, 0.100000, 0.100000, 0.100000, 0.100000, 0.100000]   ')


        child.expect('GDL> ')

        child.sendline('o-> set, fit_comp_maxima= [1.00000e+20, 8.00000, 2.00000, 2.00000, 2.00000, 2.00000,2.00000, 2.00000]')

        child.expect('GDL> ')

        child.sendline('o-> set, fit_comp_free_mask= [1B, 1B, 1B, 1B, 0B, 0B, 0B, 0B] ')

        child.expect('GDL> ')
        child.sendline('o-> set, spex_eband= [[1.02800, 1.75763], [1.75763, 3.00513], [3.00513, 5.13806], [5.13806, 8.78485], [8.78485, 15.0200]] ')

        child.expect('GDL> ')

        child.sendline('o-> set, fit_function= "vth_abun"')

        child.expect('GDL> ')

        # child.sendline('o-> set, spex_tband= [['27-Aug-2021 00:00:00.904', '27-Aug-2021 05:54:45.904'], ['27-Aug-2021 05:54:45.904', '27-Aug-2021 11:49:30.904'], ['27-Aug-2021 11:49:30.904', '27-Aug-2021 17:44:15.904'], ['27-Aug-2021 17:44:15.904', '27-Aug-2021 23:39:00.904']]')

        # child.expect('GDL> ')

        child.sendline('o -> write_model_textfile(out=o,filename="hero.txt) ')
        
        child.expect('GDL> ')
        # You can add more commands here if needed
        # For example, to run an IDL script:
        


        child.expect('GDL> ')


        # # Exit the GDL interactive environment
        # child.sendline('exit')

        # # Wait for the tcsh prompt
        # child.expect('% ')

        # Exit tcsh
        # child.sendline('exit')

        # Wait for the process to finish
        child.expect(pexpect.EOF)

        print("Automation complete.")

    except pexpect.EOF:
        print("The child process exited unexpectedly.")
    except pexpect.TIMEOUT:
        print("Timeout occurred while waiting for the child process.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    automate_ospex()
