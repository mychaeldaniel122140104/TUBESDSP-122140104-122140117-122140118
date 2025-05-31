# modules/recording.py

import os
import time
import threading
import traceback
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox
from modules.plotting import _plot_signal_subplot


def start_30s_recording(app):
    if not app.running:
        messagebox.showwarning("Warning", "Please start video feed first!")
        return

    if app.recording_30s:
        messagebox.showinfo("Info", "Recording already in progress!")
        return

    app.recording_data = {
        'raw_rgb': [],
        'rppg_filtered': [],
        'respirasi_raw': [],
        'respirasi_filtered': [],
        'timestamps': []
    }

    app.recording_30s = True
    app.recording_start_time = time.time()
    app.recording_status_text.set("Recording... 0s/30s")

    threading.Thread(target=lambda: recording_countdown(app), daemon=True).start()
    messagebox.showinfo("Recording Started", "Recording 30 seconds of signal data...")


def recording_countdown(app):
    start_time = time.time()
    while app.recording_30s and (time.time() - start_time) < 30:
        elapsed = int(time.time() - start_time)
        app.recording_status_text.set(f"Recording... {elapsed}s/30s")
        time.sleep(0.5)

    if app.recording_30s:
        app.recording_30s = False
        app.recording_status_text.set("Processing & Saving...")
        app.window.after(100, lambda: generate_30s_plots(app))


def generate_30s_plots(app):
    try:
        if not app.recording_data['timestamps']:
            messagebox.showwarning("Warning", "No data recorded!")
            app.recording_status_text.set("Ready")
            return

        output_dir = "saved_signals"
        os.makedirs(output_dir, exist_ok=True)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamps = np.array(app.recording_data['timestamps'])
        time_sec = timestamps - timestamps[0]

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'30-Second Signal Analysis - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                     fontsize=16, fontweight='bold')

        _plot_signal_subplot(axes[0, 0], time_sec, app.recording_data['raw_rgb'], 
                             'g-', "Raw RGB Green Channel Signal", "RGB Green Value (0-255)")
        _plot_signal_subplot(axes[0, 1], time_sec, app.recording_data['rppg_filtered'], 
                             'r-', "Filtered rPPG Signal (Heart Rate)", "Normalized Amplitude")
        _plot_signal_subplot(axes[1, 0], time_sec, app.recording_data['respirasi_raw'], 
                             'b-', "Raw Respiration Signal (Shoulder Y-coordinate)", "Y Coordinate (normalized)")
        _plot_signal_subplot(axes[1, 1], time_sec, app.recording_data['respirasi_filtered'], 
                             'c-', "Filtered Respiration Signal", "Filtered Amplitude")

        plt.tight_layout()
        plot_filename = os.path.join(output_dir, f"signal_analysis_{now}.png")
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.close()

        data_filename = os.path.join(output_dir, f"signal_data_{now}.txt")
        with open(data_filename, 'w') as f:
            f.write(f"# 30-Second Signal Data Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Sampling Rate: {app.fps} Hz\n")
            f.write(f"# Duration: {len(app.recording_data['timestamps'])/app.fps:.1f} seconds\n\n")
            f.write("Time(s)\tRaw_RGB\trPPG_Filtered\tRespi_Raw\tRespi_Filtered\n")

            max_len = max(len(app.recording_data[key]) for key in app.recording_data if key != 'timestamps')
            for i in range(max_len):
                time_val = time_sec[i] if i < len(time_sec) else ""
                row = [
                    time_val,
                    app.recording_data['raw_rgb'][i] if i < len(app.recording_data['raw_rgb']) else "",
                    app.recording_data['rppg_filtered'][i] if i < len(app.recording_data['rppg_filtered']) else "",
                    app.recording_data['respirasi_raw'][i] if i < len(app.recording_data['respirasi_raw']) else "",
                    app.recording_data['respirasi_filtered'][i] if i < len(app.recording_data['respirasi_filtered']) else "",
                ]
                f.write("\t".join(map(str, row)) + "\n")

        messagebox.showinfo("Save Successful", f"30-second analysis saved:\nPlot: {plot_filename}\nData: {data_filename}")

    except Exception as e:
        error_msg = f"Failed to generate plots: {str(e)}"
        messagebox.showerror("Plot Error", error_msg)
        print(f"Plot generation error: {traceback.format_exc()}")

    finally:
        app.recording_status_text.set("Ready")


def save_data(app):
    if not app.rppg_buffer and not app.respirasi_buffer:
        messagebox.showwarning("No Data", "No signal data to save. Please start monitoring first.")
        return False

    try:
        output_dir = "saved_signals"
        os.makedirs(output_dir, exist_ok=True)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"sinyal_log_{now}.txt")

        with open(filename, 'w') as f:
            f.write(f"# Signal Data Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Sampling Rate: {app.fps} Hz\n")
            f.write(f"# Buffer Size: rPPG={len(app.rppg_buffer)}, Respirasi={len(app.respirasi_buffer)}\n\n")

            f.write("# rPPG Signal (Normalized Green Channel)\n")
            for i, val in enumerate(app.rppg_buffer):
                f.write(f"{i/app.fps:.3f}\t{val:.6f}\n")

            f.write(f"\n# Respirasi Signal (Shoulder Y-coordinate)\n")
            for i, val in enumerate(app.respirasi_buffer):
                f.write(f"{i/app.fps:.3f}\t{val:.6f}\n")

        app.video_label.configure(text=f"Data berhasil disimpan ke:\n{filename}", fg="lime")
        messagebox.showinfo("Save Successful", f"Data berhasil disimpan ke:\n{filename}")
        return True

    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save data: {str(e)}")
        return False
