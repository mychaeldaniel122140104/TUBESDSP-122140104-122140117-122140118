# gui.py
"""
Modul GUI untuk aplikasi Real-time rPPG dan Respiration Rate Tracker.
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import traceback
import os
import threading
import time

from respirasi_signal import RespirasiExtractor
from rppg_signal import RPPGExtractor
from signal_filter import apply_bandpass_filter, filter_rppg_signal, filter_respiration_signal
from utils import estimate_heart_rate, estimate_respiration_rate

from modules.layout import init_layout
from modules.video_processing import start_video, stop_video, update_video
from modules.recording import start_30s_recording, save_data, recording_countdown, generate_30s_plots
from modules.plotting import update_plot, update_hr_plot, update_rr_plot, _plot_signal_subplot


class RespirasiRPPGApp:
    def __init__(self):
        self.hr_plot = None
        self.ax_hr = None
        self.canvas_hr = None
        self.rr_plot = None
        self.ax_rr = None
        self.canvas_rr = None

        self.window = tk.Tk()
        self.window.title("Realtime rPPG and Respiration Rate Tracker")
        self.window.geometry("1280x720")
        self.window.configure(bg="#2e2e2e")
        self.window.minsize(960, 600)

        self.running = False
        self.cap = None
        self.fps = 30
        self.buffer_max = 300

        try:
            self.respirasi_extractor = RespirasiExtractor()
            self.rppg_extractor = RPPGExtractor()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize extractors: {str(e)}")
            return

        self.respirasi_buffer = []
        self.rppg_buffer = []

        self.raw_rgb_buffer = []
        self.respirasi_raw_buffer = []

        self.recording_30s = False
        self.recording_start_time = None
        self.recording_data = {
            'raw_rgb': [],
            'rppg_filtered': [],
            'respirasi_raw': [],
            'respirasi_filtered': [],
            'timestamps': []
        }

        self.hr_label_text = tk.StringVar(value="-- BPM")
        self.rr_label_text = tk.StringVar(value="-- Breaths/min")
        self.recording_status_text = tk.StringVar(value="Ready")

        # Panggil layout builder dari module
        init_layout(self)

    def run(self):
        try:
            self.window.mainloop()
        except Exception as e:
            messagebox.showerror("Application Error", f"Unexpected error: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
