import tkinter as tk
import ipaddress
from tkinter import ttk
from tkinter.messagebox import showerror
from ttkthemes import ThemedTk
from tkinter import OptionMenu, StringVar
from Oscilloscope_PyVisa import Oscilloscope
import os
import multiprocessing
import logging
import matplotlib.pyplot as plt
import matplotlib.figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from PIL import ImageTk, Image


import threading
from threading import Thread
import logging
import tkinter.scrolledtext as ScrolledText

import pandas as pd
from pandas import plotting
import numpy as np
import scipy.io as sio
from scipy.io import savemat
import time

all_channels = ["C1","C2","C3","C4","C5","C6","C7","C8"]
current_directory = os.getcwd()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LeCroy Oscilloscope Controller")
        # img = ImageTk.PhotoImage(file="app_icon.png")  
        # self.iconphoto(False, img)
        # self.geometry('1600x1000')
        # self.resizable(True, True)
        # sizegrip = ttk.Sizegrip(self)
        # sizegrip.grid(row=1, sticky='s')


        '''CHANNEL'''
        options_channels = [1, 2, 3, 4, 5, 6, 7, 8]

        options_channel_units = ['V','A','others']

        options_channel_coupling = ['DC50', 'GND', 'DC1M', 'AC1M']

        '''TIMEBASE'''
        options_t_div = ['1NS','2NS','5NS','10NS','20NS','50NS','100NS','200NS','500NS','1US','2US','5US','10US','20US','50US','100US','200US','500US','1MS','2MS','5MS','10MS','20MS','50MS','100MS','200MS','500MS','1S','2S','5S','10S','20S','50S','100S']

        options_sampling_mode = ['RealTime', 'Sequence']

        options_sample_rate = ['SetMaximumMemory', 'FixedSampleRate']

        # options_max_sample_points = []

        options_active_channels = ["8","4","2","Auto"]

        '''TRIGGER'''
        options_trig_sources = ['C1','C2','C3','C4', 'C5', 'C6', 'C7', 'C8', 'Ext','Line','FastEdge']

        options_trig_types = ['EDGE', 'WIDTH', 'PATTERN', 'SMART', 'MEASUREMENT' , 'TV', 'MULTISTAGE']

        options_trig_slopes = ["Positive", "Negative", "Either"]

        options_trig_coupling = ['AC','DC','HFREJ','LFREJ']

        options_trig_modes = ['AUTO', 'NORM', 'STOP', 'SINGLE']

        click_units= StringVar()
        click_units.set(options_channel_units[0])

        click_channel_coupling = tk.StringVar()
        click_channel_coupling.set(options_channel_coupling[0])
        
        click_t_div = StringVar()
        click_t_div.set(options_t_div[0])

        click_samp_mode = StringVar()
        click_samp_mode.set(options_sampling_mode[0])

        click_samp_rate = StringVar()
        click_samp_rate.set(options_sample_rate[0])

        click_act_channels = StringVar()
        click_act_channels.set(options_active_channels[3])

        click_type = StringVar()
        click_type.set(options_trig_types[0])
        
        click_slope = StringVar()
        click_slope.set(options_trig_slopes[0])

        click_source = StringVar()
        click_source.set(options_trig_sources[0])

        click_coupling = StringVar()
        click_coupling.set(options_trig_coupling[0])

        click_mode = StringVar()
        click_mode.set(options_trig_modes[0])

        ip_address = tk.StringVar()
        timeout_value = tk.StringVar()
        select_channel = tk.StringVar
        invert_status = tk.StringVar()
        var_gain_status = tk.StringVar()
        trace_status = tk.StringVar()
        VerScale_value = tk.StringVar()
        VerOff_value = tk.StringVar()
        units_per_volt_value = tk.StringVar()
        sample_points_value = tk.StringVar()

        # Device Frame
        device_frame = tk.LabelFrame(self, text="Device", height=500, width=300)
        device_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

         # Load the image
        image = Image.open(f"{current_directory}\osc_image_gui.png")  
        # Resize the image to your desired dimensions
        image = image.resize((100, 50))  
        # Convert the Image object to a Tkinter PhotoImage object
        photo = ImageTk.PhotoImage(image)

        # Create a Label widget to display the image
        image_label = tk.Label(device_frame, image=photo)
        image_label.image = photo  # Retain a reference to the image to prevent garbage collection
        image_label.grid(row=0, column=0, sticky='nsew')

        ip_label = tk.Label(device_frame, text="IP:")
        ip_label.grid(row=1, column=0, sticky='nsew')
        ip_entry = tk.Entry(device_frame, textvariable = ip_address, width=20)
        ip_entry.grid(row=1, column=1)

        timeout_label = tk.Label(device_frame, text="Timeout:")
        timeout_label.grid(row=2, column=0)
        timeout = tk.Entry(device_frame, textvariable = timeout_value, width=20)
        timeout.grid(row=2, column=1)

        connection_status = tk.Label(device_frame, text="Status: ")
        connection_status.grid(row=3, sticky='')
       

        def connect_oscilloscope(ip_address:str):
            osc = Oscilloscope(f'TCPIP0::{ip_address}::inst0::INSTR')
            osc.read_termination = '\n'
            osc.write_termination = '\n'
            osc_connected = True
            return osc

        def is_valid_ip(ip):
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    return True
                except ValueError:
                    return False
                
        def connect_btn_thread():
            connect_thread = Thread(name= "connect", target=connect_btn_func).start()

        def connect_btn_func():
            global osc 
            if is_valid_ip(ip_entry.get()):
                osc = connect_oscilloscope(ip_entry.get())
            else:
                showerror("Unvalid IP Address", "The IP Address is not valid")

        connect_button = tk.Button(device_frame, text="Connect", command=connect_btn_thread)
        connect_button.grid(row=4, column=0)

        def disconnect_btn_thread():
            disconnect_thread = Thread(name= "disconnect", target=disconnect_btn_func).start()

        def disconnect_btn_func():
            global osc 
            if osc.connected:
                osc.disconnect()

        disconnect_button = tk.Button(device_frame, text="Disconnect", command=disconnect_btn_thread)
        disconnect_button.grid(row=4, column=1)

        osc = connect_oscilloscope("192.168.40.100")


       
        # ´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´CHANNEL FRAME´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´´


        def set_VerScale(channel:int):
            entry = VerScale_value.get()
            if entry == '':
                showerror('Error', 'No Input specified!')
            else:
                osc.set_vdiv(channel, float(entry))

        def set_VerOff(channel:int):
            entry = VerOff_value.get()
            if entry == '':
                showerror('Error', 'No Input specified!')
            else:
                osc.write(f"vbs? 'app.Acquisition.{'C'+ str(channel)}.VerOffset = {float(entry)}'")

        def set_multiplier(channel:int):
            entry = units_per_volt_value.get()
            if entry == '':
                showerror('Error', 'No Input specified!')
            else:
                osc.set_units_per_volt(channel, float(float(entry)))

        def set_chan_coupling(channel:int):
            osc.set_channel_coupling(channel, click_channel_coupling.get())

        def set_var_gain(channel:int):                             
            if var_gain_status.get() == "ON":
                osc.set_Ver_Scale_Variable_Gain(channel, True)
            else:
                osc.set_Ver_Scale_Variable_Gain(channel, False)

        def set_traces():
            e_text = trace_status.get()
            traces = e_text.split(',')
            for elem in traces:
                elem.replace('c','C')
            '''set channel traces ON/OFF'''
            if e_text == '':
                showerror('Error', 'No Input specified!')
            else:
                for trace in traces:
                    osc.set_trace(f"{trace}","ON")

                for channel in all_channels:
                    if channel not in traces:
                        osc.set_trace(f"{channel}","OFF")

        # Channel Frame
        channel_frame = tk.LabelFrame(self, text="Channel")
        channel_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        #channel settings tabs
        channel_tabs = ttk.Notebook(channel_frame)
        channel_tabs.grid()

        '''--------------------------------------------------------------------CHANNEL 1--------------------------------------------------------------------------'''
        # channel 1 widgets
        frame = ttk.Frame(channel_tabs)

        channels_label = ttk.Label(frame, text='Channels:', background='white')
        channels_entry = ttk.Entry(frame, textvariable = trace_status, width=10)
        channels_entry_button = ttk.Button(frame, text="Set", command = set_traces)

        channels_label.grid(column=0, row=0)
        channels_entry.grid(column=1, row=0)
        channels_entry_button.grid(column=2, row=0)
        
        label = ttk.Label(frame, text= str("C1"), font='bold',background='yellow')
        # trace_button = ttk.Checkbutton(frame, text='Trace On', variable=trace_status, onvalue='ON', offvalue='OFF', command= set_trace)

        VerScale_label = ttk.Label(frame, text='Vertical Scale:')
        VerScale_entry = ttk.Entry(frame, textvariable = VerScale_value, width=10)
        VerScale_button = ttk.Button(frame, text="Set", command = lambda: set_VerScale(1))
        # current_VerScale = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text= str(osc.get_vdiv(1)))

        VerOff_label = ttk.Label(frame, text='Offset:')
        VerOff_entry = ttk.Entry(frame, textvariable = VerOff_value, width=10)
        VerOff_button = ttk.Button(frame, text="Set", command = lambda: set_VerOff(1))
        # current_VerOff = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_VerOffset(1)))


        chan_coupling_label = ttk.Label(frame, text='Coupling:')
        chan_coupling_options = ttk.OptionMenu(frame, click_channel_coupling, *options_channel_coupling, command= lambda x: set_chan_coupling(1))
        # current_chan_coupling = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_ch_coupling(1)))
        
        units_per_volt_label = ttk.Label(frame, text='Units /V (slope):')
        units_per_volt_entry = ttk.Entry(frame, textvariable = units_per_volt_value, width=10)
        units_per_volt_button = ttk.Button(frame, text="Set", command = lambda: set_multiplier(1))
        # current_units_per_volt = ttk.Label(frame, width=8, borderwidth=2, relief="groove")

        var_gain_button = ttk.Checkbutton(frame, text='Var. Gain', variable=var_gain_status, onvalue='ON', offvalue='OFF', command= lambda: set_var_gain(1)) 

        # ================= CH 1 layout ====================================================================
        frame.grid(padx = 5, pady = 5)
        label.grid()
        VerScale_label.grid(row=3, column=0)
        VerScale_entry.grid(row=3, column=1)
        VerScale_button.grid(row=3, column=2)
        # current_VerScale.grid()
        VerOff_label.grid(row=4, column=0)
        VerOff_entry.grid(row=4, column=1)
        # current_VerOff.grid()
        VerOff_button.grid(row=4, column=2)

        # current_units.grid()
        units_per_volt_label.grid(row=5, column=0)
        units_per_volt_entry.grid(row=5, column=1)
        units_per_volt_button.grid(row=5, column=2)
        # current_units_per_volt.grid()
        chan_coupling_label.grid(row=6, column=0)
        chan_coupling_options.grid(row=6, column=1)
        # trace_button.grid()
        var_gain_button.grid(row=6, column=2)
        
        channel_tabs.add(frame, text=str(options_channels[0]))


        '''--------------------------------------------------------------------CHANNEL 2--------------------------------------------------------------------------'''
        # channel 2 widgets
        frame = ttk.Frame(channel_tabs)
        
        label = ttk.Label(frame, text= str("C2"), font='bold',background='#FF007F')
        # trace_button = ttk.Checkbutton(frame, text='Trace On', variable=trace_status, onvalue='ON', offvalue='OFF', command= set_trace)

        VerScale_label = ttk.Label(frame, text='Vertical Scale:')
        VerScale_entry = ttk.Entry(frame, textvariable = VerScale_value, width=10)
        VerScale_button = ttk.Button(frame, text="Set", command = lambda: set_VerScale(2))
        # current_VerScale = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text= str(osc.get_vdiv(2)))

        VerOff_label = ttk.Label(frame, text='Offset:')
        VerOff_entry = ttk.Entry(frame, textvariable = VerOff_value, width=10)
        VerOff_button = ttk.Button(frame, text="Set", command = lambda: set_VerOff(2))
        # current_VerOff = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_VerOffset(2)))


        chan_coupling_label = ttk.Label(frame, text='Coupling:')
        chan_coupling_options = ttk.OptionMenu(frame, click_channel_coupling, *options_channel_coupling, command= lambda x: set_chan_coupling(2))
        # current_chan_coupling = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_ch_coupling(2)))
        
        units_per_volt_label = ttk.Label(frame, text='Units /V (slope):')
        units_per_volt_entry = ttk.Entry(frame, textvariable = units_per_volt_value, width=10)
        units_per_volt_button = ttk.Button(frame, text="Set", command = lambda: set_multiplier(2))
        # current_units_per_volt = ttk.Label(frame, width=8, borderwidth=2, relief="groove")

        var_gain_button = ttk.Checkbutton(frame, text='Var. Gain', variable=var_gain_status, onvalue='ON', offvalue='OFF', command= lambda: set_var_gain(2)) 

        # ================= CH 2 layout ====================================================================
        frame.grid(padx = 5, pady = 5)
        label.grid()
        VerScale_label.grid(row=3, column=0)
        VerScale_entry.grid(row=3, column=1)
        VerScale_button.grid(row=3, column=2)
        # current_VerScale.grid()
        VerOff_label.grid(row=4, column=0)
        VerOff_entry.grid(row=4, column=1)
        # current_VerOff.grid()
        VerOff_button.grid(row=4, column=2)

        # current_units.grid()
        units_per_volt_label.grid(row=5, column=0)
        units_per_volt_entry.grid(row=5, column=1)
        units_per_volt_button.grid(row=5, column=2)
        # current_units_per_volt.grid()
        chan_coupling_label.grid(row=6, column=0)
        chan_coupling_options.grid(row=6, column=1)
        # trace_button.grid()
        var_gain_button.grid(row=6, column=2)
        
        channel_tabs.add(frame, text=str(options_channels[1]))

        '''--------------------------------------------------------------------CHANNEL 3--------------------------------------------------------------------------'''
        # channel 3 widgets
        frame = ttk.Frame(channel_tabs)
        
        label = ttk.Label(frame, text= str("C3"), font='bold',background='#00ffff')
        # trace_button = ttk.Checkbutton(frame, text='Trace On', variable=trace_status, onvalue='ON', offvalue='OFF', command= set_trace)

        VerScale_label = ttk.Label(frame, text='Vertical Scale:')
        VerScale_entry = ttk.Entry(frame, textvariable = VerScale_value, width=10)
        VerScale_button = ttk.Button(frame, text="Set", command = lambda: set_VerScale(3))
        # current_VerScale = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text= str(osc.get_vdiv(3)))

        VerOff_label = ttk.Label(frame, text='Offset:')
        VerOff_entry = ttk.Entry(frame, textvariable = VerOff_value, width=10)
        VerOff_button = ttk.Button(frame, text="Set", command = lambda: set_VerOff(3))
        # current_VerOff = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_VerOffset(3)))


        chan_coupling_label = ttk.Label(frame, text='Coupling:')
        chan_coupling_options = ttk.OptionMenu(frame, click_channel_coupling, *options_channel_coupling, command= lambda x: set_chan_coupling(3))
        # current_chan_coupling = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_ch_coupling(3)))
        
        units_per_volt_label = ttk.Label(frame, text='Units /V (slope):')
        units_per_volt_entry = ttk.Entry(frame, textvariable = units_per_volt_value, width=10)
        units_per_volt_button = ttk.Button(frame, text="Set", command = lambda: set_multiplier(3))
        # current_units_per_volt = ttk.Label(frame, width=8, borderwidth=2, relief="groove")

        var_gain_button = ttk.Checkbutton(frame, text='Var. Gain', variable=var_gain_status, onvalue='ON', offvalue='OFF', command= lambda: set_var_gain(3)) 

        # ================= CH 3 layout ====================================================================
        frame.grid(padx = 5, pady = 5)
        label.grid()
        VerScale_label.grid(row=3, column=0)
        VerScale_entry.grid(row=3, column=1)
        VerScale_button.grid(row=3, column=2)
        # current_VerScale.grid()
        VerOff_label.grid(row=4, column=0)
        VerOff_entry.grid(row=4, column=1)
        # current_VerOff.grid()
        VerOff_button.grid(row=4, column=2)

        # current_units.grid()
        units_per_volt_label.grid(row=5, column=0)
        units_per_volt_entry.grid(row=5, column=1)
        units_per_volt_button.grid(row=5, column=2)
        # current_units_per_volt.grid()
        chan_coupling_label.grid(row=6, column=0)
        chan_coupling_options.grid(row=6, column=1)
        # trace_button.grid()
        var_gain_button.grid(row=6, column=2)
        
        channel_tabs.add(frame, text=str(options_channels[2]))

      
        '''--------------------------------------------------------------------CHANNEL 4--------------------------------------------------------------------------'''
        # channel 4 widgets
        frame = ttk.Frame(channel_tabs)
        
        label = ttk.Label(frame, text= str("C4"), font='bold',background='#66ff00')
        # trace_button = ttk.Checkbutton(frame, text='Trace On', variable=trace_status, onvalue='ON', offvalue='OFF', command= set_trace)

        VerScale_label = ttk.Label(frame, text='Vertical Scale:')
        VerScale_entry = ttk.Entry(frame, textvariable = VerScale_value, width=10)
        VerScale_button = ttk.Button(frame, text="Set", command = lambda: set_VerScale(4))
        # current_VerScale = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text= str(osc.get_vdiv(4)))

        VerOff_label = ttk.Label(frame, text='Offset:')
        VerOff_entry = ttk.Entry(frame, textvariable = VerOff_value, width=10)
        VerOff_button = ttk.Button(frame, text="Set", command = lambda: set_VerOff(4))
        # current_VerOff = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_VerOffset(4)))


        chan_coupling_label = ttk.Label(frame, text='Coupling:')
        chan_coupling_options = ttk.OptionMenu(frame, click_channel_coupling, *options_channel_coupling, command= lambda x: set_chan_coupling(4))
        # current_chan_coupling = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_ch_coupling(4)))
        
        units_per_volt_label = ttk.Label(frame, text='Units /V (slope):')
        units_per_volt_entry = ttk.Entry(frame, textvariable = units_per_volt_value, width=10)
        units_per_volt_button = ttk.Button(frame, text="Set", command = lambda: set_multiplier(4))
        # current_units_per_volt = ttk.Label(frame, width=8, borderwidth=2, relief="groove")

        var_gain_button = ttk.Checkbutton(frame, text='Var. Gain', variable=var_gain_status, onvalue='ON', offvalue='OFF', command= lambda: set_var_gain(4)) 

        # ================= CH 4 layout ====================================================================
        frame.grid(padx = 5, pady = 5)
        label.grid()
        VerScale_label.grid(row=3, column=0)
        VerScale_entry.grid(row=3, column=1)
        VerScale_button.grid(row=3, column=2)
        # current_VerScale.grid()
        VerOff_label.grid(row=4, column=0)
        VerOff_entry.grid(row=4, column=1)
        # current_VerOff.grid()
        VerOff_button.grid(row=4, column=2)

        # current_units.grid()
        units_per_volt_label.grid(row=5, column=0)
        units_per_volt_entry.grid(row=5, column=1)
        units_per_volt_button.grid(row=5, column=2)
        # current_units_per_volt.grid()
        chan_coupling_label.grid(row=6, column=0)
        chan_coupling_options.grid(row=6, column=1)
        # trace_button.grid()
        var_gain_button.grid(row=6, column=2)
        
        channel_tabs.add(frame, text=str(options_channels[3]))



        '''--------------------------------------------------------------------CHANNEL 5--------------------------------------------------------------------------'''
        # channel 5 widgets
        frame = ttk.Frame(channel_tabs)
        
        label = ttk.Label(frame, text= str("C5"), font='bold',background='#d3d3d3')
        # trace_button = ttk.Checkbutton(frame, text='Trace On', variable=trace_status, onvalue='ON', offvalue='OFF', command= set_trace)

        VerScale_label = ttk.Label(frame, text='Vertical Scale:')
        VerScale_entry = ttk.Entry(frame, textvariable = VerScale_value, width=10)
        VerScale_button = ttk.Button(frame, text="Set", command = lambda: set_VerScale(5))
        # current_VerScale = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text= str(osc.get_vdiv(5)))

        VerOff_label = ttk.Label(frame, text='Offset:')
        VerOff_entry = ttk.Entry(frame, textvariable = VerOff_value, width=10)
        VerOff_button = ttk.Button(frame, text="Set", command = lambda: set_VerOff(5))
        # current_VerOff = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_VerOffset(5)))


        chan_coupling_label = ttk.Label(frame, text='Coupling:')
        chan_coupling_options = ttk.OptionMenu(frame, click_channel_coupling, *options_channel_coupling, command= lambda x: set_chan_coupling(5))
        # current_chan_coupling = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_ch_coupling(5)))
        
        units_per_volt_label = ttk.Label(frame, text='Units /V (slope):')
        units_per_volt_entry = ttk.Entry(frame, textvariable = units_per_volt_value, width=10)
        units_per_volt_button = ttk.Button(frame, text="Set", command = lambda: set_multiplier(5))
        # current_units_per_volt = ttk.Label(frame, width=8, borderwidth=2, relief="groove")

        var_gain_button = ttk.Checkbutton(frame, text='Var. Gain', variable=var_gain_status, onvalue='ON', offvalue='OFF', command= lambda: set_var_gain(5)) 

        # ================= CH 5 layout ====================================================================
        frame.grid(padx = 5, pady = 5)
        label.grid()
        VerScale_label.grid(row=3, column=0)
        VerScale_entry.grid(row=3, column=1)
        VerScale_button.grid(row=3, column=2)
        # current_VerScale.grid()
        VerOff_label.grid(row=4, column=0)
        VerOff_entry.grid(row=4, column=1)
        # current_VerOff.grid()
        VerOff_button.grid(row=4, column=2)

        # current_units.grid()
        units_per_volt_label.grid(row=5, column=0)
        units_per_volt_entry.grid(row=5, column=1)
        units_per_volt_button.grid(row=5, column=2)
        # current_units_per_volt.grid()
        chan_coupling_label.grid(row=6, column=0)
        chan_coupling_options.grid(row=6, column=1)
        # trace_button.grid()
        var_gain_button.grid(row=6, column=2)
        
        channel_tabs.add(frame, text=str(options_channels[4]))

        '''--------------------------------------------------------------------CHANNEL 6--------------------------------------------------------------------------'''
        # channel 6 widgets
        frame = ttk.Frame(channel_tabs)
        
        label = ttk.Label(frame, text= str("C6"), font='bold',background='#A020F0')
        # trace_button = ttk.Checkbutton(frame, text='Trace On', variable=trace_status, onvalue='ON', offvalue='OFF', command= set_trace)

        VerScale_label = ttk.Label(frame, text='Vertical Scale:')
        VerScale_entry = ttk.Entry(frame, textvariable = VerScale_value, width=10)
        VerScale_button = ttk.Button(frame, text="Set", command = lambda: set_VerScale(6))
        # current_VerScale = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text= str(osc.get_vdiv(6)))

        VerOff_label = ttk.Label(frame, text='Offset:')
        VerOff_entry = ttk.Entry(frame, textvariable = VerOff_value, width=10)
        VerOff_button = ttk.Button(frame, text="Set", command = lambda: set_VerOff(6))
        # current_VerOff = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_VerOffset(6)))


        chan_coupling_label = ttk.Label(frame, text='Coupling:')
        chan_coupling_options = ttk.OptionMenu(frame, click_channel_coupling, *options_channel_coupling, command= lambda x: set_chan_coupling(6))
        # current_chan_coupling = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_ch_coupling(6)))
        
        units_per_volt_label = ttk.Label(frame, text='Units /V (slope):')
        units_per_volt_entry = ttk.Entry(frame, textvariable = units_per_volt_value, width=10)
        units_per_volt_button = ttk.Button(frame, text="Set", command = lambda: set_multiplier(6))
        # current_units_per_volt = ttk.Label(frame, width=8, borderwidth=2, relief="groove")

        var_gain_button = ttk.Checkbutton(frame, text='Var. Gain', variable=var_gain_status, onvalue='ON', offvalue='OFF', command= lambda: set_var_gain(6)) 

        # ================= CH 6 layout ====================================================================
        frame.grid(padx = 5, pady = 5)
        label.grid()
        VerScale_label.grid(row=3, column=0)
        VerScale_entry.grid(row=3, column=1)
        VerScale_button.grid(row=3, column=2)
        # current_VerScale.grid()
        VerOff_label.grid(row=4, column=0)
        VerOff_entry.grid(row=4, column=1)
        # current_VerOff.grid()
        VerOff_button.grid(row=4, column=2)

        # current_units.grid()
        units_per_volt_label.grid(row=5, column=0)
        units_per_volt_entry.grid(row=5, column=1)
        units_per_volt_button.grid(row=5, column=2)
        # current_units_per_volt.grid()
        chan_coupling_label.grid(row=6, column=0)
        chan_coupling_options.grid(row=6, column=1)
        # trace_button.grid()
        var_gain_button.grid(row=6, column=2)
        
        channel_tabs.add(frame, text=str(options_channels[5]))



        '''--------------------------------------------------------------------CHANNEL 7--------------------------------------------------------------------------'''
        # channel 7 widgets
        frame = ttk.Frame(channel_tabs)
        
        label = ttk.Label(frame, text= str("C7"), font='bold',background='#FF0000')
        # trace_button = ttk.Checkbutton(frame, text='Trace On', variable=trace_status, onvalue='ON', offvalue='OFF', command= set_trace)

        VerScale_label = ttk.Label(frame, text='Vertical Scale:')
        VerScale_entry = ttk.Entry(frame, textvariable = VerScale_value, width=10)
        VerScale_button = ttk.Button(frame, text="Set", command = lambda: set_VerScale(7))
        # current_VerScale = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text= str(osc.get_vdiv(7)))

        VerOff_label = ttk.Label(frame, text='Offset:')
        VerOff_entry = ttk.Entry(frame, textvariable = VerOff_value, width=10)
        VerOff_button = ttk.Button(frame, text="Set", command = lambda: set_VerOff(7))
        # current_VerOff = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_VerOffset(7)))


        chan_coupling_label = ttk.Label(frame, text='Coupling:')
        chan_coupling_options = ttk.OptionMenu(frame, click_channel_coupling, *options_channel_coupling, command= lambda x: set_chan_coupling(7))
        # current_chan_coupling = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_ch_coupling(7)))
        
        units_per_volt_label = ttk.Label(frame, text='Units /V (slope):')
        units_per_volt_entry = ttk.Entry(frame, textvariable = units_per_volt_value, width=10)
        units_per_volt_button = ttk.Button(frame, text="Set", command = lambda: set_multiplier(7))
        # current_units_per_volt = ttk.Label(frame, width=8, borderwidth=2, relief="groove")

        var_gain_button = ttk.Checkbutton(frame, text='Var. Gain', variable=var_gain_status, onvalue='ON', offvalue='OFF', command= lambda: set_var_gain(7)) 

        # ================= CH 7 layout ====================================================================
        frame.grid(padx = 5, pady = 5)
        label.grid()
        VerScale_label.grid(row=3, column=0)
        VerScale_entry.grid(row=3, column=1)
        VerScale_button.grid(row=3, column=2)
        # current_VerScale.grid()
        VerOff_label.grid(row=4, column=0)
        VerOff_entry.grid(row=4, column=1)
        # current_VerOff.grid()
        VerOff_button.grid(row=4, column=2)

        # current_units.grid()
        units_per_volt_label.grid(row=5, column=0)
        units_per_volt_entry.grid(row=5, column=1)
        units_per_volt_button.grid(row=5, column=2)
        # current_units_per_volt.grid()
        chan_coupling_label.grid(row=6, column=0)
        chan_coupling_options.grid(row=6, column=1)
        # trace_button.grid()
        var_gain_button.grid(row=6, column=2)
        
        channel_tabs.add(frame, text=str(options_channels[6]))

        '''--------------------------------------------------------------------CHANNEL 8--------------------------------------------------------------------------'''
        # channel 8 widgets
        frame = ttk.Frame(channel_tabs)
        
        label = ttk.Label(frame, text= str("C8"), font='bold',background='#FFA500')
        # trace_button = ttk.Checkbutton(frame, text='Trace On', variable=trace_status, onvalue='ON', offvalue='OFF', command= set_trace)

        VerScale_label = ttk.Label(frame, text='Vertical Scale:')
        VerScale_entry = ttk.Entry(frame, textvariable = VerScale_value, width=10)
        VerScale_button = ttk.Button(frame, text="Set", command = lambda: set_VerScale(8))
        # current_VerScale = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text= str(osc.get_vdiv(8)))

        VerOff_label = ttk.Label(frame, text='Offset:')
        VerOff_entry = ttk.Entry(frame, textvariable = VerOff_value, width=10)
        VerOff_button = ttk.Button(frame, text="Set", command = lambda: set_VerOff(8))
        # current_VerOff = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_VerOffset(8)))


        chan_coupling_label = ttk.Label(frame, text='Coupling:')
        chan_coupling_options = ttk.OptionMenu(frame, click_channel_coupling, *options_channel_coupling, command= lambda x: set_chan_coupling(8))
        # current_chan_coupling = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_ch_coupling(8)))
        
        units_per_volt_label = ttk.Label(frame, text='Units /V (slope):')
        units_per_volt_entry = ttk.Entry(frame, textvariable = units_per_volt_value, width=10)
        units_per_volt_button = ttk.Button(frame, text="Set", command = lambda: set_multiplier(8))
        # current_units_per_volt = ttk.Label(frame, width=8, borderwidth=2, relief="groove")

        var_gain_button = ttk.Checkbutton(frame, text='Var. Gain', variable=var_gain_status, onvalue='ON', offvalue='OFF', command= lambda: set_var_gain(8)) 

        # ================= CH 8 layout ====================================================================
        frame.grid(padx = 5, pady = 5)
        label.grid()
        VerScale_label.grid(row=3, column=0)
        VerScale_entry.grid(row=3, column=1)
        VerScale_button.grid(row=3, column=2)
        # current_VerScale.grid()
        VerOff_label.grid(row=4, column=0)
        VerOff_entry.grid(row=4, column=1)
        # current_VerOff.grid()
        VerOff_button.grid(row=4, column=2)

        # current_units.grid()
        units_per_volt_label.grid(row=5, column=0)
        units_per_volt_entry.grid(row=5, column=1)
        units_per_volt_button.grid(row=5, column=2)
        # current_units_per_volt.grid()
        chan_coupling_label.grid(row=6, column=0)
        chan_coupling_options.grid(row=6, column=1)
        # trace_button.grid()
        var_gain_button.grid(row=6, column=2)
        
        channel_tabs.add(frame, text=str(options_channels[7]))

        #channel settings tabs
        channel_tabs = ttk.Notebook(channel_frame)
        channel_tabs.grid()


        # Timebase Frame
        timebase_frame = tk.LabelFrame(self, text="Timebase")
        timebase_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # # ========================================================================== Timebase SETUP  ===========================================================================================
        def set_samp_mode():
            osc.set_sampling_mode(click_samp_mode.get())


        def set_max_sample_pts():
            entry = sample_points_value.get()
            if entry == '':
                showerror('Error', 'No Input specified!')
            else:
                osc.set_max_sample_points(float(entry))

        def set_samp_rate():
            osc.set_sample_rate(click_samp_rate.get())

        def set_active_chans():
            osc.set_active_channels(click_act_channels.get())


        tdiv_label = ttk.Label(timebase_frame, text='Time/div:')
        drop_t_div = OptionMenu(timebase_frame, click_t_div, *options_t_div, command = osc.set_tdiv)
        # current_t_div = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text= str(Thread(target=osc.query("tdiv?")).start)) #CHECK

        sampling_mode_label = ttk.Label(timebase_frame, text='Sampling Mode:')
        sampling_mode_options = OptionMenu(timebase_frame, click_samp_mode, *options_sampling_mode)
        sampling_mode_button = ttk.Button(timebase_frame, text="Set",command=set_samp_mode)

        sampling_rate_label = ttk.Label(timebase_frame, text='Sample rate:')
        sampling_rate_options = OptionMenu(timebase_frame, click_samp_rate, *options_sample_rate)
        sampling_rate_button = ttk.Button(timebase_frame, text="Set", command = set_samp_rate)
        
        sample_points_label = ttk.Label(timebase_frame, text='Max Sample Points:')
        sample_points_entry = ttk.Entry(timebase_frame, textvariable = sample_points_value, width=10)
        sample_points_button = ttk.Button(timebase_frame, text="Set", command = set_max_sample_pts)

        active_channels_label = ttk.Label(timebase_frame, text='Active Channels:')
        active_channels_options = OptionMenu(timebase_frame, click_act_channels, *options_active_channels)
        active_channels_button = ttk.Button(timebase_frame, text="Set", command = set_active_chans)

        # middle frame (left) layout
        tdiv_label.grid(row=0, column=0)
        drop_t_div.grid(row=0, column=1)
        # current_t_div.grid()
        sampling_mode_label.grid(row=1, column=0)
        sampling_mode_options.grid(row=1, column=1)
        sampling_mode_button.grid(row=1, column=2)
        sampling_rate_label.grid(row=2, column=0)
        sampling_rate_options.grid(row=2, column=1)
        sampling_rate_button.grid(row=2, column=2)
        sample_points_label.grid(row=3, column=0)
        sample_points_entry.grid(row=3, column=1)
        sample_points_button.grid(row=3, column=2)
        active_channels_label.grid(row=4, column=0)
        active_channels_options.grid(row=4, column=1)
        active_channels_button.grid(row=4, column=2)
        

        def set_level():
            e_text = level_entry.get()
            if e_text == '':
                showerror('Error', 'No Input specified!')
            else:
                osc.set_trig_level(click_source.get(), float(e_text))  #%% Error 

        def set_delay():
            entry = delay_entry.get()
            if entry == '':
                showerror('Error', 'No Input specified!')
            else:
                osc.set_trig_delay(float(entry))

        def set_coupling():
            osc.set_trig_coupling(click_source.get(), click_coupling.get())

        def set_slope():
            osc.set_trig_slope(click_source.get(), click_slope.get())

        def recall_labNB():
            entry = recall_labNB_entry.get()
            if entry == '':
                showerror('Error', 'No Input specified!')
            else:
                osc.recall_labnotebook(entry)
        def set_invert():
            if invert_status.get() == "ON":
                osc.query(f"vbs? 'app.Acquisition.{click_source.get()}.Invert = true'")
            else:
                osc.query(f"vbs? 'app.Acquisition.{click_source.get()}.Invert = false'")

        def SET_SINGLE_TRIGGER():
            logging.info('Waiting for Trigger...')
            osc.wait_for_single_trigger()
            logging.info("Single Triggered!")

            filename = str(osc.trig_time().replace("," , "_"))
            osc.show_measure("True")
            osc.statistics_measure("True")                                                                 

            trigger_id =  filename
            logging.info(f"----------------TRIGGER ID: {filename}-------------------------")
            osc.save_labnotebook('D:/LabNotebook/', filename, save_tables=True, annotate=False)
            logging.info("LabNotebook Saved!")
            osc.set_trig_mode("AUTO")
            logging.info('Trigger Mode = AUTO\n')
            logging.info(f'[0]: Code Completed! LabNotebook Saved: {trigger_id + ".lnb"}\n\n')


        def set_trig_mode():
            osc.set_trig_mode(click_mode.get())

        

        # Trigger Frame
        trigger_frame = tk.LabelFrame(self, text="Trigger")
        trigger_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

         # ================= TRIGGER SETUP  ====================================================================

        def start_single_trigger():
            global start_single_trigger
            start_single_trigger = threading.Thread(target=SET_SINGLE_TRIGGER)
            start_single_trigger.daemon = True
            start_single_trigger.start()

        trig_type_label = ttk.Label(trigger_frame, text='Type:')
        drop_trig_types = OptionMenu(trigger_frame, click_type, *options_trig_types, command = osc.set_trig_type)
        current_trig_type = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_trig_type()))

        source_label = ttk.Label(trigger_frame, text='Source:')
        drop_sources = OptionMenu(trigger_frame, click_source, *options_trig_sources, command=osc.set_trig_source)
        current_trig_source = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_trig_source()))

        coupling_label = ttk.Label(trigger_frame, text='Coupling:')
        drop_coupling = OptionMenu(trigger_frame, click_coupling, *options_trig_coupling)
        coupling_button = ttk.Button(trigger_frame, text="Set", command = set_coupling)
        current_trig_coupling = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_trig_coupling(click_source.get())))
        
        slope_label = ttk.Label(trigger_frame, text='Slope:')
        drop_slope = OptionMenu(trigger_frame, click_slope, *options_trig_slopes)
        slope_button = ttk.Button(trigger_frame, text="Set", command = set_slope)
        current_trig_slope = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_trig_slope(click_source.get())))

        invert_button = ttk.Checkbutton(trigger_frame, text='Invert', variable=invert_status, onvalue='ON', offvalue='OFF', command=set_invert)   

        level_entry = ttk.Entry(trigger_frame, width=10)
        level_label = ttk.Label(trigger_frame, text='Level:')
        set_level_button = ttk.Button(trigger_frame, text="Set", command = set_level)
        current_trig_level = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_trig_level(click_source.get())))

        delay_label = ttk.Label(trigger_frame, text='Delay:')
        delay_entry = ttk.Entry(trigger_frame, width=10)
        set_delay_button = ttk.Button(trigger_frame,  text="Set", command = set_delay)
        current_trig_delay = ttk.Label(frame, width=8, borderwidth=2, relief="groove", text=str(osc.get_trig_delay()))

        drop_modes = OptionMenu(trigger_frame, click_mode, *options_trig_modes)
        trigger_button = ttk.Button(trigger_frame, text="Trigger", style="TButton",command = set_trig_mode)

        set_single_trigger = ttk.Label(trigger_frame, text='Single Trigger:')
        set_single_trigger_button = ttk.Button(trigger_frame, text="START", command = start_single_trigger)

        recall_labNB_label = ttk.Label(trigger_frame, text='LabNB:')
        recall_labNB_entry = ttk.Entry(trigger_frame, width=10)
        recall_labNB_button = ttk.Button(trigger_frame,  text="Recall", command = recall_labNB)

        # bottom frame (left)  layout
        trig_type_label.grid(row=0, column=0)
        drop_trig_types.grid(row=0, column=1)
        # current_trig_type.grid()
        source_label.grid(row=1, column=0)
        drop_sources.grid(row=1, column=1)
        # current_trig_source.grid()
        coupling_label.grid(row=2, column=0)
        drop_coupling.grid(row=2, column=1)
        coupling_button.grid(row=2, column=2)
        # current_trig_coupling.grid()
        slope_label.grid(row=3, column=0)
        drop_slope.grid(row=3, column=1)
        slope_button.grid(row=3, column=2)
        # current_trig_slope.grid()
        recall_labNB_label.grid(row=4, column=0)
        recall_labNB_entry.grid(row=4, column=1)
        recall_labNB_button.grid(row=4, column=2)

        level_label.grid(row=5, column=0)
        level_entry.grid(row=5, column=1)
        set_level_button.grid(row=5, column=2)
        # current_trig_level.grid()
        delay_label.grid(row=6, column=0)
        delay_entry.grid(row=6, column=1)
        set_delay_button.grid(row=6, column=2)
        # current_trig_delay.grid()
        drop_modes.grid(row=7, column=0)
        trigger_button.grid(row=7, column=1)
        # current_trig_type.grid()
        set_single_trigger.grid(row=8, column=0)
        set_single_trigger_button.grid(row=8, column=1)
        invert_button.grid(row=9, column=0)
            
        # Console Frame
        console_frame = tk.LabelFrame(self, text="Console")
        console_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        # console_text = tk.Text(console_frame, height=10, width=50)
        # console_text.pack()

        class TextHandler(logging.Handler):
        # This class allows you to log to a Tkinter Text or ScrolledText widget
        # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

            def __init__(self, text):
                # run the regular Handler __init__
                logging.Handler.__init__(self)
                # Store a reference to the Text it will log to
                self.text = text

            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text.configure(state='normal')
                    self.text.insert(tk.END, msg + '\n')
                    self.text.configure(state='disabled')
                    # Autoscroll to the bottom
                    self.text.yview(tk.END)
                # This is necessary because we can't modify the Text from other threads
                self.text.after(0, append)

            def clear(self):
                self.text.delete('1.0', tk.END)   #ADD CLEAR LOGS BUTTON

        def worker():
            # Skeleton worker function, runs in separate thread (see below)   
            while True:
                # Report time / date at 2-second intervals
                time.sleep(2)
                timeStr = time.asctime()
                msg = 'Current time: ' + timeStr
                logging.info(msg) 

        def _quit():        # stops mainloop
            self.destroy()  # this is necessary on Windows to prevent
            self.quit()     # Fatal Python Error: PyEval_RestoreThread: NULL tstate
          
        
        st = ScrolledText.ScrolledText(console_frame, state='disabled')
        st.configure(font='TkFixedFont')
        st.grid(column=2, row=3, sticky='w', columnspan=4)

        # Create textLogger
        text_handler = TextHandler(st)

        # Logging configuration
        logging.basicConfig(filename=f"{current_directory}\\test.log",
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s')        

        # Add the handler to logger
        logger = logging.getLogger()        
        logger.addHandler(text_handler)
    

        quit_button = tk.Button(console_frame, text="Quit", command=_quit, padx=5, pady=5)
        quit_button.place(relx=0.5, rely=1, anchor='s')


if __name__ == "__main__":
    t = Thread(target=App().mainloop())
    t.setDaemon(True)
    t.start()   
        
    
