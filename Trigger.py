"""
@author: DAV1SI

TRIGGER_SEQ.py triggers the OSC in SINGLE Trigger mode and automatically saves the triggered waveforms & it's parameters on the controlling PC.

This Script works with the config file "default_config.ini". Change the parameters as needed in the config file and they will be reflected on the OSC whwn you Trigger it.

"""
from SET_TRIGGER_SEQ import SET_SINGLE_TRIGGER, SET_NORMAL_TRIGGER, read_settings_config
import multiprocessing
import sys
import logging
import os

if __name__ == '__main__':
    current_working_dir = os.getcwd()
    config = read_settings_config(fr"{current_working_dir}/default_config.ini")
    timeout = float(config[1])
    # timeout = timeout_value
    # Start bar as a process
    p = multiprocessing.Process(target=SET_SINGLE_TRIGGER)
    sys.stdout.flush()
    p.start()

    # Wait for 10 seconds or until process finishes
    p.join(timeout)

    # If thread is still active
    if p.is_alive():
        logging.error(6)

        # Terminate - may not work if process is stuck for good
        p.terminate()
        # OR Kill - will work for sure, no chance for process to finish nicely however
        # p.kill()

        p.join()