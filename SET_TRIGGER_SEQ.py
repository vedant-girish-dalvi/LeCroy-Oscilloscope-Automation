"""

@author: DAV1SI

This script DEFINES the SINGLE trigger parameters of the oscilloscope and triggers, saves and retrieves the waveform & parameters

The data is saved on the controlling PC in .txt file format with a specific trigger ID.

This Script works with the config file "default_config.ini". Change the parameters as needed in the config file and they will be reflected on the OSC whwn you Trigger it.

"""

import pandas as pd
from Oscilloscope_PyVisa import Oscilloscope
from configparser import ConfigParser
import sys
import getopt
import os
import logging
logging.getLogger().setLevel(logging.INFO)
import time


#Get the configparser object
config_object = ConfigParser()

'''DEFAULT CONFIG PARAMETERS'''
def read_settings_config(filename:str):
    config_object.read(f"{filename}")
    
    ip_settings = config_object["ip address"]
    ip = ip_settings["ip"]

    timeout_settings = config_object["Timeout"]
    timeout = timeout_settings["Timeout"]

    channel_settings = config_object["Channel Settings"]
    channels_list = channel_settings["channels_list"]
    ch1_name_label = channel_settings["ch_1_name_label"]
    ch2_name_label = channel_settings["ch_2_name_label"]
    ch3_name_label = channel_settings["ch_3_name_label"]
    ch4_name_label = channel_settings["ch_4_name_label"]
    ch5_name_label = channel_settings["ch_5_name_label"]
    ch6_name_label = channel_settings["ch_6_name_label"]
    ch7_name_label = channel_settings["ch_7_name_label"]
    ch8_name_label = channel_settings["ch_8_name_label"]

    timebase_settings = config_object["Timebase Settings"]
    sampling_mode  = timebase_settings["sampling_mode"]
    tdiv  = timebase_settings["tdiv"]
    sample_rate   = timebase_settings["sample_rate"]
    max_sample_points   = timebase_settings["max_sample_points"]
    num_active_channels = timebase_settings["active_channels"]

    channel_ver_settings = config_object["Channel Vertical Settings"]
    vdiv = channel_ver_settings["vdiv"]
    ver_offset = channel_ver_settings["ver_offset"]
    units_per_volt  = channel_ver_settings["units_per_volt"]
    variable_gain_status  = channel_ver_settings["variable_gain_status"]
    channel_coupling  = channel_ver_settings["channel_coupling"]

    trigger_settings = config_object["Trigger Settings"]
    trigger_source = trigger_settings["trigger source"]
    trigger_type = trigger_settings["trigger type"]
    trigger_coupling = trigger_settings["trigger coupling"]
    trigger_slope = trigger_settings["trigger slope"]
    trigger_level = trigger_settings["trigger level"]
    trigger_delay = trigger_settings["trigger delay"]

    data_retrieval__settings = config_object["Data Retrieval"]
    source_folder  = data_retrieval__settings["source_folder"]
    target_folder   = data_retrieval__settings["target_folder"]
    
    return ip, timeout, str(channels_list), ch1_name_label, ch2_name_label, ch3_name_label, ch4_name_label, ch5_name_label, ch6_name_label, ch7_name_label, ch8_name_label, sampling_mode,tdiv, sample_rate, max_sample_points, num_active_channels, vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling, trigger_source, trigger_type, trigger_coupling, trigger_slope, trigger_level, trigger_delay, source_folder, target_folder

def myfunc(argv):
    arg_config_path = ""
    arg_setup_file = ""
    arg_help = "{0} <config_filepath> <setup_filepath>".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "h:cf:st:", ["help", "config_filepath=", "setup_filepath="])
    except: 
        print(arg_help)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-cf", "--config_filepath"):
            arg_config_path = arg
        elif opt in ("-st", "--setup_filepath"):
            arg_setup_file = arg
        
        print('config_filepath:', arg_config_path)
        print('setup_filepath:', arg_setup_file)

    
def SET_SINGLE_TRIGGER(): # OSC_path
        myfunc(sys.argv)
        
        # get the current working directory
        current_working_directory = os.getcwd()
        
        if len(sys.argv) < 2:
            #   raise FileExistsError("[1]:Please provide with Config File Path!")
            return logging.error(1)
              
        config_path = sys.argv[1]

        # if not config_path == str:
        #     raise TypeError(f'[2]:TypeError - <config_path> must be a string, received object of type {type(config_path)}.')
            #   return "[2] : Type Error ( <config_path> must be a string, received object of other type)"
        
        if ".ini" not in config_path:
            #   raise NameError("Provide correct config file extension! (.ini)")
              return logging.error(3)
        
        if not os.path.exists(config_path):
            #   raise FileExistsError("[1] : Please provide with correct Config File Path!")
               return logging.error(4)
              
        filename = sys.argv[2] if len(sys.argv) == 3 else 'setup_wb.lss'
        setup_filename = filename
        
        if ".lss" not in setup_filename:
            # raise NameError("Please provide correct setup file extension! (.lss)")
                return logging.error(3)
                
        # if not setup_filename == str:
        #     raise TypeError(f'[2]:TypeError - <setup_filename> must be a string, received object of type {type(setup_filename)}.')
        #     # return "[2] : Type Error ( <config_path> must be a string, received object of other type)"
   
        os.chdir(str(config_path.split("default")[0]))

        ip, timeout, channels_list, ch1_name_label, ch2_name_label, ch3_name_label, ch4_name_label, ch5_name_label, ch6_name_label, ch7_name_label, ch8_name_label, sampling_mode, tdiv, sample_rate, max_sample_points, active_channels, vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling, trigger_source, trigger_type, trigger_coupling, trigger_slope, trigger_level, trigger_delay, source_folder, target_folder = read_settings_config(fr"{config_path}")
        timeout = float(timeout)
        trace_status = list(channels_list.split(","))
        all_channels = ["C1","C2","C3","C4","C5","C6","C7","C8"]
        ch_names_labels = [ch1_name_label, ch2_name_label, ch3_name_label, ch4_name_label, ch5_name_label, ch6_name_label, ch7_name_label, ch8_name_label]
        # print(trace_status)
        max_sample_points = float(max_sample_points)  
        ver_offset = float(ver_offset)
        variable_gain_status = bool(variable_gain_status)
        units_per_volt = float(units_per_volt)
        trigger_level = float(trigger_level)
        trigger_delay = float(trigger_delay)

        osc = Oscilloscope(f"TCPIP0::{ip}::inst0::INSTR")

        if source_folder == "":
                if not(os.path.exists("source_folder") and os.path.isdir("source_folder")):
                        os.makedirs(f"{current_working_directory}\\source_folder")
                source_folder = f"{current_working_directory}\\source_folder"

        if target_folder == "":
                if not(os.path.exists("target_folder") and os.path.isdir(f"{current_working_directory}\\target_folder")):
                        os.makedirs("target_folder")
                target_folder = f"{current_working_directory}\\target_folder"

        if setup_filename == "setup_wb.lss":                     #if no setup_filename given via command line creates a setup file with this name  
                
                '''set channel traces ON/OFF'''
                for trace in trace_status:
                    osc.set_trace(f"{trace}","ON")

                    '''Setting channel parameters with trace ON'''
                    osc.SET_CHANNEL_PARAMETERS(int(trace.split("C")[1]), vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling)

                # for name_label in ch_names_labels:
                #       if not name_label == "":
                #             osc.set_channel_alias(name_label.split(",")[0])
                #             osc.set_channel_label(name_label.split)

                for channel in all_channels:
                    if channel not in trace_status:
                        osc.set_trace(f"{channel}","OFF")

                '''setting Timebase settings for ALL channels'''
                osc.timebase_settings(sampling_mode, tdiv, sample_rate, max_sample_points, active_channels)

                'setting ALL channel parameters'
                # osc.SET_CHANNEL_PARAMETERS(1, vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling)  #channel 1   
                # osc.SET_CHANNEL_PARAMETERS(2, vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling)  #channel 2
                # osc.SET_CHANNEL_PARAMETERS(3, vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling)  #channel 3   
                # osc.SET_CHANNEL_PARAMETERS(4, vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling)  #channel 4
                # osc.SET_CHANNEL_PARAMETERS(5, vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling)  #channel 5   
                # osc.SET_CHANNEL_PARAMETERS(6, vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling)  #channel 6
                # osc.SET_CHANNEL_PARAMETERS(7, vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling)  #channel 7   
                # osc.SET_CHANNEL_PARAMETERS(8, vdiv, ver_offset, units_per_volt, variable_gain_status, channel_coupling)  #channel 8
        
                '''Set Trigger Parameters for Trigger Source'''
                osc.set_trig_mode('AUTO')
                osc.set_trig_source(trigger_source)
                osc.set_trig_type(trigger_type)
                osc.set_trig_coupling(trigger_source,trigger_coupling)
                osc.set_trig_slope(trigger_source,trigger_slope)
                osc.set_trig_level(trigger_source,trigger_level)
                osc.set_trig_delay(trigger_delay)
                
                #save setup file on OSC @C:\LCRYDMIN\Setups\
                '''If setup file already exists, it will keep incrementing a counter and create new setup files'''
                osc.save_setup('File',True, f"{setup_filename}")
    
        elif setup_filename != "setup_wb.lss":                  #if a setup_filename corresponding to a setup on OSC is given via command line     
                #recall setup file on OSC @C:\LCRYDMIN\Setups\

                osc.recall_setup('File', f"{setup_filename}")
                logging.info("Recall Setup Successfull!")
                logging.info(".....")
        
        logging.info('Waiting for Trigger...')
        osc.wait_for_single_trigger()
        logging.info("Single Triggered!")

        filename = str(osc.trig_time().replace("," , "_"))
        osc.show_measure("True")
        osc.statistics_measure("True")
    
        '''Plot the waveforms of specified channels & save them with parameters'''
        for trace in trace_status:
            trace = int(trace.split("C")[1])                                                                                                   #set range(1,5) for 4-channel and range(1,9) for 8-channel oscilloscope respectively
                    
            # waveform = osc.get_waveform(trace)
            # waveform = pd.DataFrame(waveform)
    
            trigger_id =  filename
            logging.info(f"----------------TRIGGER ID: C{trace} = {filename}-------------------------")
                #save parameters
            # logging.info(f'Saving C{trace} waveform & parameters...\n')

            # # osc.save_waveform_on_osc("Excel", trace,  "C" + str(i) + "_" + filename)
            
            # osc.save_waveform_on_PC(source_folder, waveform,  "C" + str(trace) + "_" + filename + "_waveform")
            # osc.save_parameters_trace(source_folder, trace, "C" + str(trace) + "_" + filename + "_parameters")

            # logging.info(f' C{trace} waveform & parameters saved on PC at {source_folder}\n')

        osc.save_labnotebook('D:/LabNotebook/', filename, save_tables=True, annotate=False)
        logging.info("LabNotebook Saved!")
        osc.set_trig_mode("AUTO")
        logging.info('Trigger Mode = AUTO\n')

        #saving data with specific trigger ID in folder with same name as trigger ID
        # osc.retrieve_waveform_PC(source_folder, target_folder, trigger_id)
        
        logging.info(f'[0]: Code Completed! Trigger ID: {trigger_id}')
    
        