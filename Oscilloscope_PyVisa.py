import pyvisa as visa
import pandas as pd
import xlsxwriter
import time
import numpy as np
import shutil
import datetime
import os
import logging
import sys
# resource.setrlimit(resource.RLIMIT_STACK, (2**29,-1))
# sys.setrecursionlimit(3500)

'''Oscilloscope Class and various Oscilloscope Automation Commands as it's methods.'''
connected = False
  
def _validate_channel_number(channel):
    CHANNEL_NUMBERS = {1, 2, 3, 4, 5, 6, 7, 8}
    if not isinstance(channel, int):
        raise TypeError(f'<channel type> must be a integer, received object of type {type(channel)}')
    if channel not in CHANNEL_NUMBERS:
        raise ValueError(f'<channel> must be in {CHANNEL_NUMBERS}')
    
def _validate_t_div_value(t_div_value):
    T_DIV_VALID = {'1NS','2NS','5NS','10NS','20NS','50NS','100NS','200NS','500NS','1US','2US','5US','10US','20US','50US','100US','200US','500US','1MS','2MS','5MS','10MS','20MS','50MS','100MS','200MS','500MS','1S','2S','5S','10S','20S','50S','100S'}
    if not isinstance(t_div_value, str):
        raise TypeError(f'The times/div must be a string, received object of type {type(t_div_value)}.')
    if t_div_value.lower() not in {t.lower() for t in T_DIV_VALID}:
        raise ValueError(f'The times/div must be one of {T_DIV_VALID}, received {repr(t_div_value)}...')
    
def _validate_trig_source(trig_source):
    TRIG_SOURCES_VALID = {'C1','C2','C3','C4','C5', 'C6', 'C7', 'C8', 'Ext','Line','FastEdge'}
    if not isinstance(trig_source, str):
        raise TypeError(f'The trigger source must be a string, received object of type {type(trig_source)}.')
    if trig_source.lower() not in {t.lower() for t in TRIG_SOURCES_VALID}:
        raise ValueError(f'The trigger source must be one of {TRIG_SOURCES_VALID}, received {repr(trig_source)}...')
    
def _validate_trig_type(trig_type):
    TRIG_TYPES_VALID = {'EDGE', 'WIDTH', 'PATTERN', 'SMART', 'MEASUREMENT' , 'TV', 'MULTISTAGE'}
    if not isinstance(trig_type, str):
        raise TypeError(f'The trigger type must be a string, received object of type {type(trig_type)}.')
    if trig_type.lower() not in {t.lower() for t in TRIG_TYPES_VALID}:
        raise ValueError(f'The trigger source must be one of {TRIG_TYPES_VALID}, received {repr(trig_type)}...')
    
def _validate_waveform_format(format:str):
    FORMAT_NAMES_VALID= {'Binary','ASCII','Excel','MATLAB','MathCad'}
    if not isinstance(format, str):
        raise TypeError(f'The format type must be a string, received object of type {type(format)}')
    if format.lower() not in {t.lower() for t in FORMAT_NAMES_VALID}:
        raise ValueError(f'<FORMAT> must be one of {FORMAT_NAMES_VALID},  received {repr(format)}...')
    
class Oscilloscope:
    def __init__(self, resource_name:str):
        """This is a wrapper class for a pyvisa Resource object to communicate
        with a LeCroy oscilloscope.
        
        Parameters
        ----------
        resource_name: str
            Whatever you have to provide to `pyvisa` to open the connection
            with the oscilloscope, see [here](https://pyvisa.readthedocs.io/en/latest/api/resourcemanager.html#pyvisa.highlevel.ResourceManager.open_resource).
            Example: "USB0::0x05ff::0x1023::4751N40408::INSTR"
        """
        
        global connected
        
        if not isinstance(resource_name, str):
            # logging.error(f"[2]:TypeError - Rescource Name should be a String, received object of type {resource_name} !")
            # raise TypeError(f'<resource_name> must be a string, received object of type {type(resource_name)}')
            return logging.error(f"[2]:TypeError - Rescource Name should be a String, received object of type {resource_name} !")
        
        try:
            oscilloscope = visa.ResourceManager('@py').open_resource(resource_name)
            # oscilloscope = visa.ResourceManager('@ivi').open_resource(resource_name)
            connected = True
            print(f"Connection to Oscilloscope {resource_name} successfull \n")
        # except visa.errors.VisaIOError:
        #     logging.error("[5]:Check OSC physical connection to PC and verify IP address!")
            # try:
            #     oscilloscope = visa.ResourceManager('@ivi').open_resource(resource_name)
            #     # visa.ResourceManager('@py').open_resource(resource_name) 
            #     connected = True
            #     print(f"Connection to Oscilloscope {resource_name} successfull \n")
            # except:
            #     connected = False
            #     pass
            #     logging.error("[5]:Check OSC physical connection to PC and verify IP address!")
            # oscilloscope = visa.ResourceManager('@ivi').open_resource(resource_name)
        except OSError as e:
            if 'Could not open VISA library' in str(e):
                oscilloscope = visa.ResourceManager('@py').open_resource(resource_name)
                connected = False
                logging.error("[5]:Check OSC physical connection to PC and verify IP address!")
            else:
                raise e
            connected = False
            return logging.error("[5]:Check OSC physical connection to PC and verify IP address!")
        
        self.resource = oscilloscope
        self.write('CHDR OFF') # This is to receive only numerical data in the answers and not also the echo of the command and some other stuff. See p. 22 of http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf
        if 'lecroy' not in self.idn.lower():
            return logging.error(f'[5]:The instrument you provided does not seem to be a LeCroy oscilloscope, its name is {self.idn}. Please check this.')
            # raise RuntimeError(f'[5]:The instrument you provided does not seem to be a LeCroy oscilloscope, its name is {self.idn}. Please check this.')


    @property
    def idn(self):
        """Returns the name of the instrument, i.e. its answer to the
        command "*IDN?"."""
        return  self.query('*IDN?')
    
    def trig_time(self):
        """Returns the date and time of the instrument, i.e. when the waveform was triggered."""
        return  self.query('DATE?')
    
    def set_osc_time(self, value:str):
        """Set the DATE/TIME of the instrument."""
        self.write(f"VBS 'app.Utility.DateTimeSetup.CurrentDateAndTime = {value}'")

    def set_osc_time_SNTP(self):
        """Set the DATE/TIME of the instrument via SNTP."""
        self.write("VBS 'app.Utility.DateTimeSetup.SetFromSNTP'")

    def write(self, msg):
        """Sends a command to the instrument."""
        self.resource.write(msg)
    
    def read(self):
        """Reads the answer from the instrument."""
        response = self.resource.read()
        if response[-1] == '\n':
            response = response[:-1]
        return response
    
    def query(self, msg):
        """Sends a command to the instrument and immediately reads the
        answer."""
        self.write(msg)
        time.sleep(0.5)
        return self.read()
    
    def get_waveform(self, channel: int):
        """Gets the waveform from the specified channel.
        
        Arguments
        ---------
        channel: int
            Number of channel from which to get the waveform data.
        
        Returns
        -------
        waveform(s): dict or list
            If the "sampling mode" is not "Sequence", a dictionary of the 
            form `{'Time (s)': numpy.array, 'Amplitude (V)': numpy.array}`
            is returned with the waveform.
            If "sampling mode" "Sequence" is configured in the oscilloscope
            then a list of dictionaries is returned, each element of the
            list being each waveform from each sequence.
        """
        _validate_channel_number(channel)
        
        # Page 223: http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf
        # Page 258: http://cdn.teledynelecroy.com/files/manuals/wr2_rcm_revb.pdf
        self.write(f'C{channel}:WF?')
        raw_data = list(self.resource.read_raw())
        
        seq = self.query('SEQUENCE?')
        sequence_status = seq.split(',')[0]
        n_segments_configured = int(seq.split(',')[1])
        n_segments_acquired = 0 if sequence_status=='OFF' else int(self.query("VBS? 'return=app.Acquisition.Horizontal.AcquiredSegments'")) # See https://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf p. 1-20.
        
        raw_data = raw_data[:-1] # For some reason last sample always seems to be some random garbage.
        raw_data = raw_data[16*(n_segments_acquired)+361:] # Here I drop the first "n" samples which are garbage, same as the last one. Don't know the reason for this. This linear function of `n_sequences` I found it empirically.
        
        volts = np.array(raw_data).astype(float)
        volts[volts>127] -= 255
        volts[volts>127-1] = float('NaN') # This means that (very likely) there was overflow towards positive voltages.
        volts[volts<128-255+1] = float('NaN') # This means that (very likely) there was overflow towards negative voltages.
        volts = volts/25*self.get_vdiv(channel)-float(self.query(f'C{channel}:ofst?'))
        
        number_of_samples_per_waveform = int(self.query("VBS? 'return=app.Acquisition.Horizontal.NumPoints'")) # See https://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf p. 1-20.
        if sequence_status == 'ON':
            number_of_samples_per_waveform += 2 # Don't ask... Without this it fails. I discovered this by try and failure.
            volts = [volts[n_waveform*number_of_samples_per_waveform:(n_waveform+1)*number_of_samples_per_waveform] for n_waveform in range(n_segments_acquired)]
        else:
            volts = [volts]
            
        #print(len(volts))
        tdiv = float(self.query('TDIV?'))
        sampling_rate = float(self.query("VBS? 'return=app.Acquisition.Horizontal.SamplingRate'")) # This line is a combination of http://cdn.teledynelecroy.com/files/manuals/maui-remote-control-and-automation-manual.pdf and p. 1-20 http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf
        times = np.arange(len(volts[0]))/sampling_rate + tdiv*14/2 # See page 223 in http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf
        
        if sequence_status == 'OFF':
            return {'Time (s)': times, 'Amplitude (V)': volts[0]}
        else:
            return [{'Time (s)': times, 'Amplitude (V)': v} for v in volts]
    
    def get_triggers_times(self, channel: int)->list:
        """Gets the trigger times (with respect to the first trigger). What
        this function returns is the list of numbers you find if you go
        in the oscilloscope window to "Timebase→Sequence→Show Sequence Trigger Times...→since Segment 1"
        
        Arguments
        ---------
        channel: int
            Number of channel from which to get the data.
        
        Returns
        -------
        trigger_times: list
            A list of trigger times in seconds from the first trigger.
        """
        _validate_channel_number(channel)
        raw = self.query(f"VBS? 'return=app.Acquisition.Channels(\"C{channel}\").TriggerTimeFromRef'") # To know this command I used the `XStream Browser` app in the oscilloscope's desktop.
        raw = [int(i) for i in raw.split(',') if i != '']
        datetimes = [datetime.datetime.fromtimestamp(i/1e10) for i in raw] # Don't know why we have to divide by 1e10, but it works...
        datetimes = [i-datetimes[0] for i in datetimes]
        return [i.total_seconds() for i in datetimes]
    
    def wait_for_single_trigger(self,timeout=-1):
        """Sets the trigger in 'SINGLE' and blocks the execution of the
        program until the oscilloscope triggers.
        - timeout: float, number of seconds to wait until raising a 
        RuntimeError exception. If timeout=-1 it is infinite."""
        try:
            timeout = float(timeout)
        except:
            raise TypeError(f'<timeout> must be a float number, received object of type {type(timeout)}.')
        self.set_trig_mode('SINGLE')
        start = time.time()
        while self.query('TRIG_MODE?') != 'STOP':
            time.sleep(.1)
            if timeout >= 0 and time.time() - start > timeout:
                raise RuntimeError(f'Timed out waiting for oscilloscope to trigger after {timeout} seconds.')
            
    def set_normal_trigger(self,timeout=5):
        """Sets the trigger in 'NORMAL' and triggers the signal multiple times
        on the same condition until Stopped manually.
        - timeout: float, number of seconds to wait until raising a 
        RuntimeError exception. If timeout=-1 it is infinite."""
        try:
            timeout = float(timeout)
        except:
            raise TypeError(f'<timeout> must be a float number, received object of type {type(timeout)}.')
        self.set_trig_mode('NORM')
        #start = time.time()
        #while self.query('TRIG_MODE?') != 'STOP':
        time.sleep(5)
        self.set_trig_mode('STOP')
            #if timeout >= 0 and time.time() - start > timeout:
            #    raise RuntimeError(f'Timed out waiting for oscilloscope to trigger after {timeout} seconds.')

    def set_trig_mode(self, mode: str):
        """Sets the trigger mode."""
        OPTIONS = ['AUTO', 'NORM', 'STOP', 'SINGLE']
        if mode.upper() not in OPTIONS:
            raise ValueError('<mode> must be one of ' + str(OPTIONS))
        self.write('TRIG_MODE ' + mode)
    
    def set_vdiv(self, channel: int, vdiv: float):
        """Sets the vertical scale for the specified channel."""
        if not isinstance(vdiv, float):
            raise TypeError(f'<vdiv> must be a float number, received object of type {type(vdiv)}.')
        _validate_channel_number(channel)
        self.write(f'C{channel}:VDIV \"{vdiv}\" ') # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=47
    
    def set_tdiv(self, tdiv: str):
        _validate_t_div_value(tdiv)
        """Sets the horizontal scale per division for the main window."""
        # See http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=151
        self.write(f'TDIV {tdiv}')

    def get_vdiv(self, channel: int):
        """Gets the vertical scale of the specified channel. Returns a 
        float number with the volts/div value."""
        _validate_channel_number(channel)
        return float(self.query(f'C{channel}:VDIV?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=47
    
    def get_tdiv(self):
        """Get the horizontal scale of the specified channel. Returns a 
        float number with the times/div value."""
        return float(self.query(f'TIME_DIV?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=151
    
    def set_VerOffset(self, channel:int, value:float):
        """Set the vertical Offset of the specified channel"""
        _validate_channel_number(channel)
        if not isinstance(value, float):
            raise TypeError(f'Vertical Offset must be a float number, received object of type {type(value)}.')
        self.write(f"vbs 'app.Acquisition.C{channel}.VerOffset = {value}'")

    def get_VerOffset(self, channel:int):
        """Get the vertical Offset of the specified channel"""
        _validate_channel_number(channel)
        return float(self.query(f'C{channel}:OFFSET?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=43
    
    def get_ch_coupling(self, channel:int):
        """Get the channel coupling of the specified channel"""
        _validate_channel_number(channel)
        return str(self.query(f'C{channel}:COUPLING?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=42
    
    def get_trig_coupling(self, trig_source:str):
        """Get the trigger coupling of the specified trig_source"""
        _validate_trig_source(trig_source)
        return str(self.query(f'{trig_source}:TRIG_COUPLING?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=160
    
    def get_trig_level(self, trig_source:str):
        """Get the trigger level of the specified trig_source"""
        _validate_trig_source(trig_source)
        return str(self.query(f'{trig_source}:TRIG_LEVEL?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=161
    
    def get_trig_delay(self):
        """Get the trigger delay"""
        return str(self.query('TRIG_DELAY?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=152
    
    def get_trig_slope(self, trig_source:str):
        """Get the trigger slope of the specified trig_source"""
        _validate_trig_source(trig_source)
        return str(self.query(f'{trig_source}:TRIG_SLOPE?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=173
    
    def get_trig_mode(self):
        """Get the trigger mode"""
        return str(self.query('TRIG_MODE?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=165
    
    def get_trig_type(self):
        """Get the trigger type"""
        return str(self.query('TRIG_PATTERN?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=167
    
    def get_sample_rate(self):
        """Get the sample rate"""
        return str(self.query('DI:SARA?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=32

    def set_Ver_Scale_Variable_Gain(self, channel:int, value:bool):
        """Set the Vertical Variable Gain On/Off of the specified channel"""
        _validate_channel_number(channel)
        if not isinstance(value, bool):
            raise TypeError(f'Vertical Variable Gain must be a Bool Value, received object of type {type(value)}.')
        self.write(f"vbs 'app.Acquisition.C{channel}.VerScaleVariable = {value}'")
    
    def set_channel_coupling(self, channel:int, value:str):
        """Set the coupling of the specified channel"""
        channel_coupling_VALID = ['DC50', 'Gnd', 'DC1M', 'AC1M']
        _validate_channel_number(channel)
        if not isinstance(value, str):
            raise TypeError(f'Vertical Offset must be a string Value, received object of type {type(value)}.')
        if not isinstance(value, str) or value.lower() not in {tc.lower() for tc in channel_coupling_VALID}:
            raise ValueError(f'The trigger coupling must be one of {channel_coupling_VALID}, received {repr(value)}...')
        self.write(f"vbs 'app.Acquisition.C{channel}.Coupling = \"{value}\" '")
                   
    def set_trig_type(self, type: str):
        """Sets the trigger type as a string."""
        # See http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf#page=40
        _validate_trig_type(type)
        string = "VBS 'app.Acquisition.Trigger.Type = "
        string += '"' + type + '"'
        string += "'"                                     
        self.write(string)
    
    def get_trig_source(self):
        """Returns the trigger source as a string."""
        # See http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf#page=34
        return str(self.query("VBS? 'return=app.Acquisition.Trigger.Source'"))
    
    def set_trig_source(self, source: str):
        """Sets the trigger source (C1, C2, Ext, etc.)."""
        # See http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf#page=34
        _validate_trig_source(source)
        string = "VBS 'app.Acquisition.Trigger.Source = "
        string += '"' + source + '"'
        string += "'"
        self.write(string)
    
    def set_trig_coupling(self, trig_source: str, trig_coupling: str):
        """Set the trigger coupling (DC, AC, etc.)."""
        # See http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf#page=37
        _validate_trig_source(trig_source)
        VALID_TRIG_COUPLINGS = {'AC','DC','HFREJ','LFREJ'}
        if not isinstance(trig_coupling, str) or trig_coupling.lower() not in {tc.lower() for tc in VALID_TRIG_COUPLINGS}:
            raise ValueError(f'The trigger coupling must be one of {VALID_TRIG_COUPLINGS}, received {repr(trig_coupling)}...')
        string = f"VBS 'app.Acquisition.Trigger.{trig_source}.Coupling = "
        string += '"' + trig_coupling + '"'
        string += "'"
        self.write(string)
    
    def set_trig_level(self, trig_source: str, level: float):
        """Set the trigger level."""
        # See http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf#page=36
        _validate_trig_source(trig_source)
        if not isinstance(level, (float, int)):
            raise ValueError(f'The trigger level must be a float number, received object of type {type(level)}.')
        string = f"VBS 'app.Acquisition.Trigger.{trig_source}.Level = "
        string += '"' + str(level) + '"'
        string += "'"
        self.write(string)
    
    def set_trig_slope(self, trig_source: str, trig_slope: str):
        """Set the trigger slope (Positive, negative, either)."""
        # See http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf#page=36
        _validate_trig_source(trig_source)
        VALID_TRIG_SLOPES = {'Positive', 'Negative', 'Either'}
        if not isinstance(trig_slope, str) or trig_slope.lower() not in {tslp.lower() for tslp in VALID_TRIG_SLOPES}:
            raise ValueError(f'The trigger coupling must be one of {VALID_TRIG_SLOPES}, received {repr(trig_slope)}...')
        string = f"VBS 'app.Acquisition.Trigger.{trig_source}.Slope = "
        string += '"' + trig_slope + '"'
        string += "'"
        self.write(string)
    
    def set_trig_delay(self, trig_delay: float):
        """Set the trig delay, i.e. the time interval between the trigger event and the center of the screen."""
        # See http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=152
        if not isinstance(trig_delay, (float)):
            raise ValueError(f'The trigger delay must be a number, received object of type {type(trig_delay)}.')
        self.write(f'TRIG_DELAY {trig_delay}')
    
    def sampling_mode_sequence(self, status:str, number_of_segments:int=None)->None:
        """Configure the "sampling mode sequence" in the oscilloscope. See
        [here](https://cdn.teledynelecroy.com/files/manuals/maui-remote-control-automation_27jul22.pdf#%5B%7B%22num%22%3A1235%2C%22gen%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C54%2C743.25%2C0%5D).
        
        Arguments
        ---------
        status: str
            Either 'on' or 'off'.
        number_of_segments: int
            Number of segments, i.e. number of "sub triggers" within the
            sequence mode.
        """
        if not isinstance(status, str) or status.lower() not in {'on','off'}:
            raise ValueError(f'`status` must be a string, either "on" or "off", received {status} of type {type(status)}.')
        if number_of_segments is not None and not isinstance(number_of_segments, int):
            raise TypeError(f'{number_of_segments} must be an integer number.')
        cmd = f'SEQUENCE {status.upper()}'
        if number_of_segments is not None:
            cmd += f',{number_of_segments}'
        self.write(cmd)
    
    def set_sequence_timeout(self, sequence_timeout:float, enable_sequence_timeout:bool=True):
        """Configures the "Sequence timeout" in the oscilloscope both value
        and enable/disable.
        
        Arguments
        ---------
        sequence_timeout: float
            Timeout value in seconds.
        enable_sequence_timeout: bool, default `True`
            Enable or disable the sequence timeout functionality.
        """
        if not isinstance(sequence_timeout, (int,float)):
            raise TypeError(f'`sequence_timeout` must be a float number, received object of type {type(sequence_timeout)}.')
        if not enable_sequence_timeout in {True, False}:
            raise TypeError(f'`enable_sequence_timeout` must be a boolean, received object of type {type(enable_sequence_timeout)}.')
        enable_sequence_timeout = 'true' if enable_sequence_timeout==True else 'false'
        self.write(f"VBS 'app.Acquisition.Horizontal.SequenceTimeout = {sequence_timeout}'")
        self.write(f"VBS 'app.Acquisition.Horizontal.SequenceTimeoutEnable = {enable_sequence_timeout}'")

    def set_trace(self, source: str, status: str):
        """Set the channel trace to ON/OFF."""
        # See http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf#page=29
        if not isinstance(source, str):
            raise TypeError(f'<source> must be a float number, received object of type {type(source)}.')
        string = f"VBS 'app.Acquisition.{source}.View = '"
        if status == "ON":
            string += "True"
        else:
            string +=  "False"
        self.write(string)
    
    def set_units_per_volt(self, channel: int, value: float):
        """Sets the units/volt for the specified channel."""
        if not isinstance(value, float):
                raise TypeError(f'<value> must be a float number, received object of type {type(value)}.')
        _validate_channel_number(channel)
        self.write(f"vbs? 'app.Acquisition.C{channel}.Multiplier = {value}'") 
         # See http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf#page=348
        
    def set_Vertical_Unit(self,channel:int,value:str):    
        """Sets the vertical unit for the specified channel."""
        Vertical_Unit_NAMES_VALID = ['V', 'A', 'Others']
        _validate_channel_number(channel)
        if not isinstance(value, str):
            raise TypeError(f'Vertical unit must be a string, received object of type {type(value)}.')
        if value.lower() not in {t.lower() for t in Vertical_Unit_NAMES_VALID}:
             raise ValueError(f'Vertical unit must be one of {Vertical_Unit_NAMES_VALID},  received {repr(value)}...')
        self.write(f"vbs? 'app.Acquisition.C{channel}.Unit = {value}'") 

    def set_channel_Bandwidth_Limit(self, channel:int, value:str):
        """Sets the Bandwidth Limit for the specified channel."""
        Limit_NAMES_VALID = ['Full', '500MHz', '200MHz','350MHz', '20MHz', '1GHz']
        _validate_channel_number(channel)
        if not isinstance(value, str):
            raise TypeError(f'<channel Bandwidth> must be a string, received object of type {type(value)}.')
        if value.lower() not in {t.lower() for t in Limit_NAMES_VALID}:
             raise ValueError(f'<channel Bandwidth> must be one of {Limit_NAMES_VALID},  received {repr(value)}...')
        self.write(f"vbs? 'app.Acquisition.Channels(C{str(channel)}).BandwidthLimit = \"{value}\")'")

    def set_channel_alias(self, channel:int, alias:str):
        """Set the channel alias"""
        _validate_channel_number(channel)
        if not isinstance(alias, str):
            raise TypeError(f'<channel alias> must be a string, received object of type {type(alias)}.')
        self.write(f"vbs? 'app.Acquisition.C{channel}.Alias = \"{alias}\"'")

    def remove_channel_alias(self, channel:int):
        """Removes the channel alias"""
        self.write(f"vbs? 'app.Acquisition.C{channel}.RemoveAlias'") 
    
    def set_channel_label(self, channel:int, label:str, view_label:bool):
        """Set the channel label"""
        _validate_channel_number(channel)
        if not isinstance(label, str):
            raise TypeError(f'<channel label> must be a string, received object of type {type(label)}.')
        self.write(f"vbs? 'app.Acquisition.C{channel}.LabelsText = \"{label}\"'")  
        self.write(f"vbs? 'app.Acquisition.C{channel}.ViewLabels = {view_label}'")

    def show_measure(self, bool:bool):
        """Show the measure table"""
        self.write(f"vbs? 'app.Measure.ShowMeasure = {bool}'") 
    
    def statistics_measure(self, bool:bool):
        """Show the statistics of the measure table"""
        self.write(f"vbs? 'app.Measure.StatsOn = {bool}'") 

    def histogram_measure(self, bool:bool):
        """Show the Histogram of the measure table"""
        self.write(f"vbs? 'app.Measure.HistoOn = {bool}'") 

    def set_measure_source(self, source:str):
        """Set the source for the measure table"""
        self.write(f"vbs? 'app.Measure.P1.Source1 = {source}'") 

    def measure_clear_sweeps(self):
        '''Clear Measure Sweeps'''
        self.write("vbs? 'app.Measure.ClearSweeps'")

    def set_sampling_mode(self, sampling_mode:str):
        '''Set the Sampling Mode'''
        sampling_mode_NAMES_VALID = ['RealTime', 'Sequence']
        if not isinstance(sampling_mode, str):
            raise TypeError(f'The format type must be a string, received object of type {type(sampling_mode)}')
        if sampling_mode.lower() not in {t.lower() for t in sampling_mode_NAMES_VALID}:
             raise ValueError(f'<sampling_mode> must be one of {sampling_mode_NAMES_VALID},  received {repr(sampling_mode)}...')
        self.write(f"vbs 'app.Acquisition.Horizontal.SampleMode = \"{sampling_mode}\" '")

    def set_sample_rate(self, sample_rate:str):
        '''Set Maximum Memory/Fixed Sample Rate'''
        sample_rate_NAMES_VALID = ['SetMaximumMemory', 'FixedSampleRate']
        if not isinstance(sample_rate, str):
            raise TypeError(f'The format type must be a string, received object of type {type(sample_rate)}')
        if sample_rate.lower() not in {t.lower() for t in sample_rate_NAMES_VALID}:
            raise ValueError(f'<real_time_memory> must be one of {sample_rate_NAMES_VALID},  received {repr(sample_rate)}...')
        self.write(f"vbs 'app.Acquisition.Horizontal.Maximize = \"{sample_rate}\" '")

    def set_max_sample_points(self, sample_points:float):
        '''Set Maximum Sample Points'''
        if not isinstance(sample_points, float):
            raise TypeError(f'The format type must be a float number, received object of type {type(sample_points)}')
        self.write(f"vbs 'app.Acquisition.Horizontal.MaxSamples = \"{sample_points}\" '")

    def set_active_channels(self, active_channels:str):
        '''Set Active Channels'''
        active_channels_NAMES_VALID = ["8","4","2","Auto"]
        if not isinstance(active_channels, str):
            raise TypeError(f'The format type must be a string, received object of type {type(active_channels)}')
        if active_channels.lower() not in {t.lower() for t in active_channels_NAMES_VALID}:
             raise ValueError(f'<active_channels> must be one of {active_channels_NAMES_VALID},  received {repr(active_channels)}...')
        self.write(f"VBS 'app.Acquisition.Horizontal.ActiveChannels = \"{active_channels}\"'")

    def timebase_settings(self, sampling_mode:str,t_div:str, real_time_memory:str, sample_points:float, active_channels:str):
        """Set all the Timebase parameters"""
        #Set the Sampling Mode
        sampling_mode_NAMES_VALID = ['RealTime', 'Sequence']
        if not isinstance(sampling_mode, str):
            raise TypeError(f'The format type must be a string, received object of type {type(sampling_mode)}')
        if sampling_mode.lower() not in {t.lower() for t in sampling_mode_NAMES_VALID}:
             raise ValueError(f'<sampling_mode> must be one of {sampling_mode_NAMES_VALID},  received {repr(sampling_mode)}...')
        self.write(f"vbs 'app.Acquisition.Horizontal.SampleMode = {sampling_mode}'")
        # #Set the Sampling Rate
        # #sample_rate_VALID = ["1000", "1250", "2500", "5000", "6250", "10000", "12500, "25000"].....]
        # if not isinstance(sampling_rate, str):
        #     raise TypeError(f'The format type must be a string, received object of type {type(sampling_rate)}')
        # self.write(f"vbs 'app.Acquisition.Horizontal.SamplingRate = {sampling_rate}'")
        #Set the Times/div
        if not isinstance(t_div, str):
            raise TypeError(f'The format type must be a string, received object of type {type(t_div)}')
        self.write(f'TDIV {t_div}')
        #Set Maximum Memory/Fixed Sample Rate
        real_time_memory_NAMES_VALID = ['SetMaximumMemory', 'FixedSampleRate']
        if not isinstance(real_time_memory, str):
            raise TypeError(f'The format type must be a string, received object of type {type(real_time_memory)}')
        if real_time_memory.lower() not in {t.lower() for t in real_time_memory_NAMES_VALID}:
             raise ValueError(f'<real_time_memory> must be one of {real_time_memory_NAMES_VALID},  received {repr(real_time_memory)}...')
        self.write(f"vbs 'app.Acquisition.Horizontal.Maximize = {real_time_memory}'")
        #Set Maximum Sample Points
        if not isinstance(sample_points, float):
            raise TypeError(f'The format type must be a float number, received object of type {type(sample_points)}')
        self.write(f"vbs 'app.Acquisition.Horizontal.MaxSamples = {sample_points}'")
        # Set Active Channels
        active_channels_NAMES_VALID = ["8","4","2","Auto"]
        if not isinstance(active_channels, str):
            raise TypeError(f'The format type must be a string, received object of type {type(active_channels)}')
        if active_channels.lower() not in {t.lower() for t in active_channels_NAMES_VALID}:
             raise ValueError(f'<active_channels> must be one of {active_channels_NAMES_VALID},  received {repr(active_channels)}...')
        self.write(f"vbs 'app.Acquisition.Horizontal.ActiveChannels = {active_channels}'")

    def save_parameters_trace(self, path:str, channel: int, id:str):
        '''MEASURES AND SAVES THE StdVer PARAMETERS OF THE TRIGGERED/SPECIFIED CHANNEL AND SAVES THEM IN A TEXT FILE 
        WITH FILENAME == TRIGGER ID'''

        """measure the parameters of the trace for the specified channel."""
        _validate_channel_number(channel)

        # See http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=101
        '''Std.Vertical Measure'''
        pkpk = self.query(f"C{channel}:PAVA? PKPK")
        pkpk = str(pkpk).replace(",OK"," V")
        pkpk = str(pkpk).replace(",NP"," V")
        ampl = self.query(f"C{channel}:PAVA? AMPL")
        ampl = str(ampl).replace(",OK"," V")
        ampl = str(ampl).replace(",NP"," V")
        
        '''Std.Horizontal Measure'''
        freq =self.query(f"C{channel}:PAVA? FREQ")
        freq = str(freq).replace(",OK"," Hz") 
        freq = str(freq).replace(",NP"," Hz")
        duty = self.query(f"C{channel}:PAVA? DUTY")
        duty = str(duty).replace(",OK"," %")
        duty = str(duty).replace(",NP"," %")

        parameters = [pkpk, ampl, freq, duty]

        if not os.path.exists(path):
                os.makedirs(path)

        id = id + ".txt"
        with open(os.path.join(path,id), 'w') as file:
            for element in parameters:
                file.write(element + '\n')

        # # print("Saving waveform data in text file on controlling PC....")
        # parameters.to_csv(os.path.join(path,id), index=False)

        # print("Saving measured parameters...")
        #dir = self.query("vbs? 'app.SaveRecall.Waveform.WaveformDir '")
        # create a new XLSX workbook
        
        # wb = xlsxwriter.Workbook(fr"{path}\{id}.xlsx")
        # worksheet_ver = wb.add_worksheet()
        # worksheet_hor = wb.add_worksheet()
        # worksheet = wb.add_worksheet()
        # insert value in the cells
        # for row_num, param in enumerate(ver_parameters):
        #     worksheet_ver.write_string(row_num,0,param)
        
        # for row_num, param in enumerate(hor_parameters):
        #     worksheet_hor.write_string(row_num,0,param)
        
        # worksheet.write(0,0,"Parameter")
        # worksheet.write(0,1,"Value")
        # worksheet.write(1,0,pkpk.split(",")[0])
        # worksheet.write(1,1,str(pkpk.split(",")[1]) + "V")
        # worksheet.write(2,0,ampl.split(",")[0])
        # worksheet.write(2,1,str(ampl.split(",")[1]) + "V")
        # worksheet.write(3,0,max.split(",")[0])
        # worksheet.write(3,1,str(max.split(",")[1]) + "V")
        # worksheet.write(4,0,min.split(",")[0])
        # worksheet.write(4,1,str(min.split(",")[1]) + "V")
        # worksheet.write(3,0,freq.split(",")[0])
        # worksheet.write(3,1,str(freq.split(",")[1]) + "Hz")
        # worksheet.write(4,0,duty.split(",")[0])
        # worksheet.write(4,1,str(duty.split(",")[1]) + "%")


        # for row_num, param in enumerate(parameters):
        #     worksheet.write_string(row_num,0,param)
        # wb.close()

        # print("Parameters saved successfully!\n")
        return 

    def save_waveform_on_OSC(self, fileformat:str, channel:int, filename:str):
        '''SAVES THE WAVEFORM DISPLAYED ON THE OSC SCREEN IN THE SPECIFIED FORMAT & PATH ON THE OSC'''
        # print("Saving waveform data on OSC....")
        self.write(f"vbs 'app.SaveRecall.Waveform.WaveFormat = \"{fileformat}\" '")
        self.write(f"vbs 'app.SaveRecall.Waveform.SaveSource = \"C{channel}\" '")
        self.query("vbs? 'app.SaveRecall.Waveform.SaveFile'")
        self.query("vbs? 'app.SaveRecall.Waveform.EnableCounterSuffix = false'")
        self.query("vbs? 'app.SaveRecall.Waveform.EnableSourcePrefix = false'")
        self.query(f"vbs? 'app.SaveRecall.Waveform.TraceTitle = \"{filename}\" '")
        #self.query("vbs? 'app.SaveRecall.Utilities.Directory")                      
        self.query("vbs? 'app.SaveRecall.Utilities.Directory'")
        # print("Waveform data saved successfully on Oscilloscope!")
    
    def get_waveform_from_osc(self, id:str):        # %%% CHECK 
        osc_path = self.read("vbs?' app.SaveRecall.Utilities.DestDirectory'")
        # print(osc_path)
        #self.write("vbs' app.SaveRecall.Utilities.DestDirectory'")
       #file_path = r"C:\Users\DAV1SI\Desktop\test"
       #os.path.join(osc_path, id)
        # print("FIle saved successfuly on PC\n")
    
    def save_waveform_on_PC(self, path:str, waveform:pd.DataFrame, id:str): #CHECK
        # '''SAVES WAVEFROM DATA ON CONTROLLING PC IN .CSV or .TXT FILE'''
        # if max_sample_points <= 1.0e+6:
        #     '''FOR SAMPLE POINTS <= 1.0 million samples, SAVE IN .CSV FILE'''
        #     if not os.path.exists(path):
        #         os.makedirs(path)
        #     id = id + ".xlsx"
        #     # print("Saving waveform data in excel on controlling PC....")
            
        #    # Determine the middle row index
        #     # middle_index = len(waveform) // 2

        #     # Highlight the middle row
        #     # waveform.loc[middle_index] = waveform.loc[middle_index, 1].apply(lambda x: f'Trigger Point:{x}')

        #     # waveform.loc[middle_index, 2] = "Trigger_Point"
        #     # waveform.style.apply(self.highlight_cells, axis=0)
        #     path = os.path.join(path,id)
        #     waveform.to_excel(path, index=False) 

        #     wb = load_workbook(path)
        #     ws = wb.active
        #     sheet = wb['Sheet1']

        #     # Get the total number of rows
        #     total_rows = sheet.max_row
        
        #     # Get the row index of the middle row
        #     middle_row_index = total_rows // 2
        #     middle_row_index = str(f"A{middle_row_index}")
    
        #     green = PatternFill(fill_type="solid", start_color="133700")
        #     ws[middle_row_index].fill = green
        #     wb.save(f"{path}")
    
        #     # print("Waveform data saved successfully on controlling PC!\n")
        # else:
        '''FOR SAMPLE POINTS > 1.0 million samples, SAVE IN .TXT FILE'''
        if not os.path.exists(path):
            os.makedirs(path)

        id = id + ".txt"
        # print("Saving waveform data in text file on controlling PC....")
        waveform.to_csv(os.path.join(path,id), index=False)

        data_file = os.path.join(path, id)
        data_file = str(data_file)
        # print(data_file)
        with open(data_file, 'r') as file:
            contents = file.readlines()

        # Find the index of the middle row
        middle_row_index = len(contents) // 2
        # print(middle_row_index)

        # Insert the custom float value after the middle row
        custom_value = "Trigger \n" # Change this to your desired custom float value
        contents.insert(middle_row_index + 1, custom_value)

        # Write the updated data back to the file
        with open(data_file, 'w') as file:
            contents = "".join(contents)
            # ('\n'.join(''.join(elems) for elems in contents))
            file.writelines(contents)
        
        # print("Waveform data saved in text file successfully on controlling PC!\n")
                
        
    def save_setup(self, save_to:str, counter_suffix:bool, filename:str):
        '''SAVES THE OSC SETUP IN FILE OR MEMORY'''
        save_to_NAMES_VALID = ['File', 'Memory']
        if not isinstance(save_to, str):
             raise TypeError(f'The format type must be a string, received object of type {type(save_to)}')
        if save_to.lower() not in {t.lower() for t in save_to_NAMES_VALID}:
             raise ValueError(f'<save_to> must be one of {save_to_NAMES_VALID},  received {repr(save_to)}...')
        '''Save setup to File or Memory'''
        self.write(f"VBS 'app.SaveRecall.Setup.SaveTo =  \"{save_to}\"")
        self.write(f"VBS 'app.SaveRecall.Setup.EnableCounterSuffix = \"{counter_suffix}\"'")
        self.write(f"VBS 'app.SaveRecall.Setup.SaveSetupFilename =  \"{filename}\"'")
        self.write(f"VBS 'app.SaveRecall.Setup.DoSaveSetupFileDoc2'")

    def recall_setup(self, recall_from:str, filename:str):
        '''RECALLS THE OSC SETUP IN FILE OR MEMORY'''
        recall_from_NAMES_VALID = ['File', 'Memory']
        if not isinstance(recall_from, str):
             raise TypeError(f'The format type must be a string, received object of type {type(recall_from)}')
        if recall_from.lower() not in {t.lower() for t in recall_from_NAMES_VALID}:
             raise ValueError(f'<recall_from> must be one of {recall_from_NAMES_VALID},  received {repr(recall_from)}...')
        '''Save setup to File or Memory'''
        self.write(f"VBS 'app.SaveRecall.Setup.RecallFrom =  \"{recall_from}\"'")
        self.write(f"VBS 'app.SaveRecall.Setup.RecallSetupFilename =  \"{filename}\"'")
        self.write(f"VBS 'app.SaveRecall.Setup.DoRecallSetupFileDoc2'")

    def save_labnotebook(self, folder_path:str, filename:str, save_tables:bool, annotate:bool):
        '''Save the Trace as a LabNotebook on the OSC'''
        if not isinstance(folder_path, str):
            raise TypeError(f'The format type must be a string, received object of type {type(folder_path)}')
        if not isinstance(filename, str):
            raise TypeError(f'The format type must be a string, received object of type {type(filename)}')
        if not isinstance(save_tables, bool):
            raise TypeError(f'The format type must be a boolean, received object of type {type(save_tables)}')
        if not isinstance(annotate, bool):
            raise TypeError(f'The format type must be a boolean, received object of type {type(annotate)}')
        self.write(f"VBS 'app.LabNotebook.ExtractFilepath = \"{folder_path}\"'")
        self.write(f"VBS 'app.LabNotebook.EnableAutoNamingCounter = False'")
        self.write(f"VBS 'app.LabNotebook.ScribbleBeforeSaving = \"{annotate}\"'")
        # self.write(f"VBS 'app.LabNotebook.SaveTables = \"{save_tables}\"'")
        self.write(f"VBS 'app.LabNotebook.SaveFilename = \"{filename}\"'")
        self.write("VBS 'app.LabNotebook.Save'")

    def recall_labnotebook(self, filename:str):
        '''recall the Trace as a LabNotebook on the OSC'''
        if not isinstance(filename, str):
            raise TypeError(f'The format type must be a string, received object of type {type(filename)}')
        
        if '.lnb' in filename:
            self.write(f"VBS 'app.LabNotebook.RecallFilename = \"{filename}\"'")
        else:
            self.write(f"VBS 'app.LabNotebook.RecallFilename = \"{filename + str('.lnb')}\"'")
        self.write("VBS 'app.LabNotebook.InternalView'")
        self.write("VBS 'app.LabNotebook.InternalViewEnable = True'")
        self.write("VBS 'app.LabNotebook.FlashBackToRecord'")
        
    def retrieve_waveform_PC(self, source_folder:str, target_folder:str, id:str):
        '''RETRIVE A WAVEFORM WITH SPECIFIC TRIGGER-ID/CHANNEL NAME AND SAVE IT IN A SEPERATE FOLDER
         WITH THE SAME NAME ON THE CONTROLLING PC'''
        if not isinstance(id, str):
                raise TypeError(f'The format type must be a string, received object of type {type(id)}')
        if " " in source_folder:
            raise NameError(f"There is a space in source folder name! Give folder name WIHTOUT a space.")
        if " " in target_folder:
            raise NameError(f"There is a space in target folder name! Give folder name WIHTOUT a space.")
        
        # Iterate through all files in the source folder
        for filename in os.listdir(source_folder):
            if id in filename:
                # Determine the destination folder
                destination_folder = os.path.join(target_folder, id)
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)

                # Move the file to the destination folder
                source_path = os.path.join(source_folder, filename)
                target_path = os.path.join(destination_folder, filename)
                shutil.copy(source_path, target_path)
                print(f"Saved {filename} to {target_path}") 

    def SET_CHANNEL_PARAMETERS(self, channel:float, v_div:float, ver_offset:float, units_per_volt:float, VerScaleVariable:bool, channel_coupling:str):
        '''SET THE Volts/Div., Variable Gain and CHannel Coupling of a Specific Channel'''
        self.set_vdiv(channel, v_div)
        self.set_VerOffset(channel, ver_offset)
        self.set_Ver_Scale_Variable_Gain(channel, VerScaleVariable)
        self.set_channel_coupling(channel, channel_coupling)
        # self.set_channel_Bandwidth_Limit(channel,BandwidthLimit)   #does not work
        self.set_units_per_volt(channel, units_per_volt)  
        # self.set_Vertical_Unit(channel, unit)        #only works for "ANYTHING" to "V"

    def SET_SINGLE_TRIGGER(self, traces): # OSC_path
    
        logging.info('Waiting for Trigger...')
        self.wait_for_single_trigger()
        logging.info("Single Triggered!")

        filename = str(self.trig_time().replace("," , "_"))
        self.show_measure("True")
        self.statistics_measure("True")
    
        '''Plot the waveforms of specified channels & save them with parameters'''
        for trace in traces:
            trace = int(trace.split("C")[1])                                                                                           
    
            trigger_id =  filename
            logging.info(f"----------------TRIGGER ID: C{trace} = {filename}-------------------------")


        self.save_labnotebook('D:/LabNotebook/', filename, save_tables=True, annotate=False)
        logging.info("LabNotebook Saved!")
        self.set_trig_mode("AUTO")
        logging.info('Trigger Mode = AUTO\n')
        logging.info(f'[0]: Code Completed! Trigger ID: {trigger_id}')
        

    