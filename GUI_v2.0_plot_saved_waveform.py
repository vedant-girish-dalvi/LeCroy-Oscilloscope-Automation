from SET_TRIGGER_SEQ import read_settings_config
import tkinter as tk
# import threading
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import os
import logging

def _quit():        # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
    root.quit()     # Fatal Python Error: PyEval_RestoreThread: NULL tstate

def clear_waveform(): #CHECK
    plt.clf()

def plot_data():
       
    # Read data from the txt file
    data_file_path = filedialog.askopenfilename(title="Select Data file", filetypes=(("TEXT files", "*.txt"), ("All files", "*.*")))
    params_id = data_file_path.split("_waveform.txt")[0]
    params_id = params_id + "_parameters.txt"
    # print(params_id)

    # Read the values from the saved text file
    
    with open(params_id, 'r') as file:
        lines = file.readlines()

    # Remove newline characters from each line
    cleaned_lines = [line.strip() for line in lines]
    
   
    if not os.path.exists(data_file_path):# or os.path.exists(params)):
        logging.error("Error: File does not exist")

    else:
        logging.debug(f"Selected File: {data_file_path}")

    with open(data_file_path, 'r') as file:
        lines = file.readlines()

    # Extract Time and Amplitude data from the file
    time = []
    amplitude = []
    for line in lines[1:]:  # Skip the header
        parts = line.strip().split(',')
        if parts[0] == "Trigger":
            continue
        else:
            time.append(float(parts[0]))
            amplitude.append(float(parts[1]))

    #Plot the data
    fig = plt.figure(figsize=(4,2))
    fig.add_subplot()    
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().delete("all")
    canvas.get_tk_widget().pack(fill='both', expand=1)

    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    toolbar.pack()

    # Plot the data
    plt.plot(time, amplitude)
    # plt.axvline(x=time//2, color = "g", ls = "--", label = "Trigger Point")
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (V)')
    plt.title(f'Saved Waveform: {data_file_path}')
    plt.grid(True)
    
    # Plot each line of text
    for i, line in enumerate(cleaned_lines):
        plt.text(0.0, 0.05*i, line, fontsize=10, transform=plt.gcf().transFigure, color="r")
        plt.subplots_adjust(left=0.11)
        #plt.text(0.006, 1.6-i*0.4, line, color="r")#,bbox=dict(facecolor='red', alpha=0.5))

    # plt.legend(loc = "upper left")


if __name__ == "__main__":
 
     # Create main window
    root = tk.Tk()
    # root.geometry("{}x{}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.geometry('300x200')
    root.state("zoomed")
    root.title("Oscilloscope Data Plotter")
    style = ttk.Style()
    style.configure("Trigger.TButton", foreground='red', background = "white", font = "Segoe UI")

    # Set the canvas size
    # canvas_width = 500
    # canvas_height = 400

    # Open label and button
    open_label = ttk.Label(root, text="Select Data File", font=('Segoe UI', 10))
    open_label.pack(padx=10, pady=10)

    open_button = ttk.Button(root, text="Open File", command=plot_data)
    open_button.pack(padx=5, pady=5)
    
    selected_file_label = tk.Label(root, text="Selected Waveform:")
    selected_file_label.pack(padx=10, pady=10)
   
    # clear_waveform_button = ttk.Button(root, text='Clear', command=clear_waveform)
    # clear_waveform_button.pack(padx=5, pady=5)

    quit_button = tk.Button(master=root, text="Quit", command=_quit)
    quit_button.pack(padx=5, pady=5)
    
    root.resizable(True, True) 
    # Run the GUI event loop
    root.mainloop()
