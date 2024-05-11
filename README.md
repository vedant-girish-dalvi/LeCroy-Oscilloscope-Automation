# **LeCroy-Oscilloscope-Automation**

The purpose of this application is to automate and customize the setup and trigger functionalities of an Oscilloscope.

`Oscilloscope_PyVisa.py` has the Oscilloscope Wrapping Class using PyVisa.

`SET_TRIGGER_SEQ.py` has all the configurable Channel, Timebase and Trigger parameters to trigger the OSC in SINGLE or NORMAL mode and save the triggered waveforms & it's parameters on the controlling PC..

`TRIGGER_SEQ.py` calls the SINGLE or NORMAL trigger functions in SET_TRIGGER.py and parameters from the 'default_config.ini' file to trigger the Scope in the respective modes and save it's waveform and parameters on controlling PC.

`GUI_v2.0_plot_saved_waveform.py` then validates the saved waveforms and parameters on the PC.

`GUI_v3.0.py` is a complete standalone application for setting different OSC parameters, triggering the Signal, running the Trigger Automation & saving the results in a LabNb file on OSC.  

------------------------------------------------------------------------------------------------------------------------------------------
## **OSCILLOSCOPE SETUP INSTRUCTIONS:**

i. Copy the latest folder of scripts from zip folder on shared drive to controlling PC. Create a new conda environment with python=3.8 and install all the dependencies with "pip install -r pip_requirements.txt" command.

ii. Now, switch ON the OSC and prepare your test setup.

iiii. Make sure Firewall is Disabled on BOTH the OSC and PC

iv. REMEMBER to set the correct IP of OSC and select the LXI(VXI1) protocol from "Utilities-> Utilities Setup-> Remote-> Control From" in DSO application on OSC. Make sure OSC and PC have the same subnet

v. Check if OSC can be pinged via Command Prompt with: `ping <ip_address>`

## **TROUBLESHOOTING**

If you cannot connect ping OSC from PC,

a. check Ethernet Connection
b. check IP address and IP subnet of OSC & PC & make sure subnet is SAME for BOTH
c. Turn Firewall OFF on OSC
d. Check remote protocol as LXI

------------------------------------------------------------------------------------------------------------------------------------------
## **TO RUN THE AUTOMATION GUI:**

Run the `GUI_v3.0.py` script.

1. Connect the OSC to the test setup.
2. Change all the parameters as required from GUI and hit "START" button
3. The LabNb is saved on the OSC with an ID which will be displayed on the GUI Console.

! [GUI 3.0](https://github.com/vedantdalvi7/LeCroy-Oscilloscope-Automation/blob/main/images/GUI_v3.0.png?raw=true)

------------------------------------------------------------------------------------------------------------------------------------------

## **TO RUN CONFIG FILE AUTOMATION SCRIPT: You need the `TRIGGER_SEQ.py` script to Trigger the OSC in SINGLE or NORMAL mode**

> Note: To change the Trigger parameters, you only need to change the Config parameters in the config file.

1. Set the individual channel Vertical & Horizontal settings using the "SET_CHANNEL_PARAMETERS" & "timebase_settings" attributes of Oscilloscope Library in `SET_TRIGGER_SEQ.py` and save the setup file as a "File" or "Memory"  in oscilloscope with a specific name/date in a specific folder.

2.The same setup can be used the next time the OSC is used by recalling this saved setup file via "recall_setup" function.

!Comment out the save and recall setup commands when not needed

3. **Change the directory to the folder containing the scripts and Run the code with the following command and args:**

`python TRIGGER_SEQ.py <config_filepath> <setup_filename (optional)`
       
USE `python TRIGGER_SEQ.py --help` for reproducing this structure on the command line interface.
Specify the correct paths to save the waveform & parameter files on OSC and controlling PC. Also, you
can use retrieve_waveform function to get waveforms with specific ID's and store them in another folder 
of your choice with the same folder name as the Trigger ID.


4. Use `GUI_v2.0_plot_saved_waveform.py` script with following command:

`python GUI_v2.0_plot_saved_waveform.py`
