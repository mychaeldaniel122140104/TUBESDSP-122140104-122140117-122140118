# gui.py
"""
Penjelas dan Penangguang jawab code GUI tampilan aplikasi : Ichsan Kuntadi Baskara
Modul ini berisi kelas utama RespirasiRPPGApp yang menangani antarmuka pengguna,
pengaturan video, pengambilan sinyal, dan integrasi plotting serta perekaman data.

Keterangan Library yang digunakan:
tkinter = Library standar Python untuk membuat Graphical User Interface (GUI), digunakan membuat jendela aplikasi, tombol, label, dan elemen UI lainnya. tkinter.messagebox menampilkan dialog pesan seperti error atau informasi.
PIL (Pillow) = Library untuk manipulasi gambar, Image dan ImageTk digunakan untuk membuka, memproses, dan menampilkan gambar di dalam GUI Tkinter.
cv2 (OpenCV) = Library komputer visi dan pemrosesan video/gambar, digunakan untuk menangkap video dari kamera dan mengolah frame video secara real-time.
matplotlib = Library untuk membuat grafik dan plotting data. FigureCanvasTkAgg mengintegrasikan grafik matplotlib ke dalam aplikasi Tkinter agar bisa tampil di GUI.
numpy = Library untuk operasi array dan komputasi numerik yang efisien, digunakan untuk pengolahan sinyal dan manipulasi data numerik seperti buffer sinyal.
datetime = Modul standar Python untuk bekerja dengan tanggal dan waktu, digunakan untuk memberikan timestamp pada data perekaman.
traceback = Modul standar Python untuk mengambil informasi detail traceback error, membantu menampilkan rincian kesalahan saat terjadi exception.
os = Modul standar Python untuk operasi sistem file dan direktori, digunakan mengelola penyimpanan data hasil perekaman dan file.
threading = Modul standar Python untuk menjalankan proses secara paralel (multithreading), berguna agar proses video capture dan GUI tetap responsif tanpa freeze.
time = Modul standar Python untuk fungsi terkait waktu seperti delay dan pengukuran durasi.
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
    """
    Pada kode ini, kelas RespirasiRPPGApp mengatur antarmuka pengguna dan logika aplikasi.
    Kelas ini menginisialisasi komponen GUI, menangani pengambilan video, ekstraksi sinyal rPPG dan respirasi,
    
    """
    def __init__(self):
        # Inisialisasi atribut utama aplikasi / plot heart rate dan respiration rate
        self.hr_plot = None
        self.ax_hr = None
        self.canvas_hr = None
        self.rr_plot = None
        self.ax_rr = None
        self.canvas_rr = None
        # Inisialisasi jendela utama aplikasi
        self.window = tk.Tk()
        self.window.title("Realtime rPPG and Respiration Rate Tracker")
        self.window.geometry("1280x720")
        self.window.configure(bg="#2e2e2e")
        self.window.minsize(960, 600)
        # Inisialisasi variabel untuk menangani video capture, status aplikasi, dan buffer sinyal
        # Inisialisasi variabel utama aplikasi, 
        # running : Status pengambilan video dan pemrosesan sinyal
        # cap : Objek VideoCapture OpenCV untuk menangkap video dari kamera
        # fps : Frame per detik untuk video
        # buffer_max : Ukuran maksimum buffer untuk menyimpan sinyal
        self.running = False
        self.cap = None
        self.fps = 30
        self.buffer_max = 300

        # Inisialisasi objek ekstraktor sinyal rPPG dan respirasi
        # Jika terjadi error saat inisialisasi, tampilkan pesan error
        try:
            self.respirasi_extractor = RespirasiExtractor()
            self.rppg_extractor = RPPGExtractor()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize extractors: {str(e)}")
            return

        # Inisialisasi buffer untuk menyimpan sinyal rPPG dan respirasi
        self.respirasi_buffer = []
        self.rppg_buffer = []
        
        self.raw_rgb_buffer = []
        self.respirasi_raw_buffer = []
        # Inisialisasi variabel untuk status perekaman (30 detik)
        self.recording_30s = False
        self.recording_start_time = None
        self.recording_data = {
            'raw_rgb': [],
            'rppg_filtered': [],
            'respirasi_raw': [],
            'respirasi_filtered': [],
            'timestamps': []
        }
        # Inisialisasi variabel untuk menyimpan nilai heart rate dan respiration rate
        self.hr_label_text = tk.StringVar(value="-- BPM")
        self.rr_label_text = tk.StringVar(value="-- Breaths/min")
        self.recording_status_text = tk.StringVar(value="Ready")

        # Panggil layout builder dari module
        init_layout(self)

    def run(self):
        """
        Menjalankan main loop aplikasi GUI.

        Menangani exception tak terduga dan memastikan resource dibersihkan saat aplikasi
        ditutup.
        """
        try:
            self.window.mainloop()
        except Exception as e:
            messagebox.showerror("Application Error", f"Unexpected error: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Membersihkan resource saat aplikasi ditutup.

        Melepas objek video capture dan menutup semua jendela OpenCV.
        """
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Entry point aplikasi, membuat instance dan menjalankan GUI
    app = RespirasiRPPGApp()
    app.run()
