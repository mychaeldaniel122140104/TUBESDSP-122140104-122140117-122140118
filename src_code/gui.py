# gui.py - Modified version with 30-second signal plotting
"""
Modul GUI untuk aplikasi Real-time rPPG dan Respiration Rate Tracker.
Versi modifikasi dengan fitur plotting dan penyimpanan grafik 30 detik.

Fitur tambahan:
- Buffer untuk raw RGB signal
- Buffer untuk respirasi sebelum dan sesudah filter
- Fungsi plotting dan penyimpanan grafik 30 detik
- Tombol untuk mulai recording 30 detik

Author: [Nama Tim]
Date: [Tanggal]
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
from signal_filter import (
    apply_bandpass_filter,
    filter_rppg_signal,
    filter_respiration_signal
)
from utils import estimate_heart_rate, estimate_respiration_rate


class RespirasiRPPGApp:
    """
    Kelas utama untuk aplikasi Real-time rPPG dan Respiration Rate Tracker.
    
    Aplikasi ini menggunakan webcam untuk menangkap video real-time dan 
    mengekstrak sinyal rPPG (remote photoplethysmography) dari dahi serta 
    sinyal respirasi dari pergerakan bahu untuk menghitung heart rate dan 
    respiration rate.
    
    Attributes yang ditambahkan:
        raw_rgb_buffer (list): Buffer untuk sinyal RGB mentah
        respirasi_raw_buffer (list): Buffer untuk sinyal respirasi sebelum filter
        recording_30s (bool): Status recording 30 detik
        recording_start_time (float): Waktu mulai recording
        recording_data (dict): Data yang direkam selama 30 detik
    """
    
    def __init__(self):
        """
        Inisialisasi aplikasi GUI dan semua komponen yang diperlukan.
        """
        self.window = tk.Tk()
        self.window.title("Realtime rPPG and Respiration Rate Tracker")
        self.window.geometry("1280x720")
        self.window.configure(bg="#2e2e2e")
        self.window.minsize(960, 600)

        # Status dan konfigurasi
        self.running = False
        self.cap = None
        self.fps = 30  # Frame rate untuk processing sinyal
        self.buffer_max = 300  # ~10 detik data pada 30 FPS

        # Inisialisasi extractor
        try:
            self.respirasi_extractor = RespirasiExtractor()
            self.rppg_extractor = RPPGExtractor()
        except Exception as e:
            messagebox.showerror("Initialization Error", 
                               f"Failed to initialize extractors: {str(e)}")
            return

        # Buffer untuk menyimpan sinyal (existing)
        self.respirasi_buffer = []
        self.rppg_buffer = []

        # Buffer tambahan untuk 30 detik recording
        self.raw_rgb_buffer = []  # RGB mentah sebelum normalisasi
        self.respirasi_raw_buffer = []  # Respirasi sebelum filter
        
        # 30 detik recording state
        self.recording_30s = False
        self.recording_start_time = None
        self.recording_data = {
            'raw_rgb': [],
            'rppg_filtered': [],
            'respirasi_raw': [],
            'respirasi_filtered': [],
            'timestamps': []
        }

        # Variabel untuk label teks
        self.hr_label_text = tk.StringVar(value="-- BPM")
        self.rr_label_text = tk.StringVar(value="-- Breaths/min")
        self.recording_status_text = tk.StringVar(value="Ready")

        # Inisialisasi layout GUI
        self.init_layout()

    def run(self):
        """
        Menjalankan aplikasi GUI.
        """
        try:
            self.window.mainloop()
        except Exception as e:
            messagebox.showerror("Application Error", f"Unexpected error: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Membersihkan resource yang digunakan aplikasi.
        """
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def init_layout(self):
        """
        Inisialisasi layout dan komponen GUI dengan tombol recording tambahan.
        """
        # Konfigurasi grid layout
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=3)
        self.window.columnconfigure(1, weight=2)

        # Title
        title = tk.Label(self.window, text="Realtime rPPG and Respiration Rate Tracker",
                         font=("Helvetica", 16, "bold"), fg="cyan", bg="#2e2e2e")
        title.grid(row=0, column=0, columnspan=2, pady=10)

        # Video frame
        self.video_frame = tk.Frame(self.window, bg="black")
        self.video_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.video_frame.rowconfigure(0, weight=1)
        self.video_frame.columnconfigure(0, weight=1)

        self.video_label = tk.Label(self.video_frame, 
                                  text="Tekan START untuk memulai feed kamera", 
                                  fg="white", bg="black")
        self.video_label.grid(sticky="nsew")

        # Panel kanan untuk grafik
        self.right_panel = tk.Frame(self.window, bg="#1e1e1e")
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.rowconfigure(0, weight=1)
        self.right_panel.rowconfigure(1, weight=1)
        self.right_panel.rowconfigure(2, weight=0)  # Status recording
        self.right_panel.columnconfigure(0, weight=1)

        # Build plots
        self.build_hr_plot()
        self.build_rr_plot()
        
        # Recording status
        self.recording_status_label = tk.Label(self.right_panel, 
                                             textvariable=self.recording_status_text,
                                             fg="yellow", bg="#1e1e1e", 
                                             font=("Arial", 10, "bold"))
        self.recording_status_label.grid(row=2, column=0, pady=5)

        # Tombol kontrol (modified)
        button_frame = tk.Frame(self.window, bg="#2e2e2e")
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        start_btn = tk.Button(button_frame, text="▶ START", command=self.start_video,
                              bg="lime green", fg="white", font=("Arial", 12, "bold"), width=12)
        start_btn.pack(side=tk.LEFT, padx=10)

        stop_btn = tk.Button(button_frame, text="⏹ STOP", command=self.stop_video,
                             bg="tomato", fg="white", font=("Arial", 12, "bold"), width=12)
        stop_btn.pack(side=tk.LEFT, padx=10)

        # Tombol baru untuk recording 30 detik
        record_btn = tk.Button(button_frame, text="📊 RECORD 30s", command=self.start_30s_recording,
                               bg="orange", fg="white", font=("Arial", 12, "bold"), width=15)
        record_btn.pack(side=tk.LEFT, padx=10)

        save_btn = tk.Button(button_frame, text="💾 SIMPAN", command=self.save_data,
                             bg="dodger blue", fg="white", font=("Arial", 12, "bold"), width=12)
        save_btn.pack(side=tk.LEFT, padx=10)

    def build_hr_plot(self):
        """
        Membuat grafik untuk menampilkan sinyal heart rate (rPPG).
        """
        frame = tk.Frame(self.right_panel, bg="#1e1e1e")
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        title = tk.Label(frame, text="❤️ Heart Rate", fg="deeppink", bg="#1e1e1e", 
                        font=("Arial", 12, "bold"))
        title.pack()

        fig, ax = plt.subplots(figsize=(4, 2))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        
        self.hr_plot, = ax.plot([], [], color='deeppink', linewidth=2)
        self.ax_hr = ax
        self.ax_hr.set_title("-- BPM", color='deeppink', fontsize=12, fontweight='bold')
        self.ax_hr.set_xlabel("Time (s)", color='white')
        self.ax_hr.set_ylabel("Amplitude", color='white')
        
        self.canvas_hr = FigureCanvasTkAgg(fig, master=frame)
        self.canvas_hr.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def build_rr_plot(self):
        """
        Membuat grafik untuk menampilkan sinyal respiration rate.
        """
        frame = tk.Frame(self.right_panel, bg="#1e1e1e")
        frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        title = tk.Label(frame, text="💨 Respiration Rate", fg="cyan", bg="#1e1e1e", 
                        font=("Arial", 12, "bold"))
        title.pack()

        fig, ax = plt.subplots(figsize=(4, 2))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        
        self.rr_plot, = ax.plot([], [], color='cyan', linewidth=2)
        self.ax_rr = ax
        self.ax_rr.set_title("-- Breaths/min", color='cyan', fontsize=12, fontweight='bold')
        self.ax_rr.set_xlabel("Time (s)", color='white')
        self.ax_rr.set_ylabel("Amplitude", color='white')
        
        self.canvas_rr = FigureCanvasTkAgg(fig, master=frame)
        self.canvas_rr.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start_video(self):
        """
        Memulai capture video dari webcam dan processing real-time.
        """
        if not self.running:
            try:
                # Coba buka kamera
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise Exception("Cannot access camera. Please check if camera is connected and not used by other applications.")
                
                # Set resolusi kamera untuk performa optimal
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                
                self.running = True
                self.video_label.configure(text="")
                
                # Clear buffer saat start ulang
                self.respirasi_buffer.clear()
                self.rppg_buffer.clear()
                self.raw_rgb_buffer.clear()
                self.respirasi_raw_buffer.clear()
                
                self.update_video()
                
            except Exception as e:
                error_msg = f"Failed to start camera: {str(e)}"
                self.video_label.configure(
                    text=error_msg, 
                    fg="red", 
                    wraplength=400
                )
                messagebox.showerror("Camera Error", error_msg)
                self.running = False
                if self.cap:
                    self.cap.release()
                    self.cap = None

    def stop_video(self):
        """
        Menghentikan capture video dan processing.
        """
        self.running = False
        self.recording_30s = False  # Stop recording juga
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.configure(
            image='', 
            text="Feed dihentikan. Tekan START untuk mulai lagi.", 
            fg="white"
        )
        self.recording_status_text.set("Ready")

    def start_30s_recording(self):
        """
        Memulai recording data sinyal selama 30 detik.
        """
        if not self.running:
            messagebox.showwarning("Warning", "Please start video feed first!")
            return
            
        if self.recording_30s:
            messagebox.showinfo("Info", "Recording already in progress!")
            return
        
        # Reset recording data
        self.recording_data = {
            'raw_rgb': [],
            'rppg_filtered': [],
            'respirasi_raw': [],
            'respirasi_filtered': [],
            'timestamps': []
        }
        
        self.recording_30s = True
        self.recording_start_time = time.time()
        self.recording_status_text.set("Recording... 0s/30s")
        
        # Start countdown thread
        threading.Thread(target=self.recording_countdown, daemon=True).start()
        
        messagebox.showinfo("Recording Started", "Recording 30 seconds of signal data...")

    def recording_countdown(self):
        """
        Thread untuk countdown recording 30 detik.
        """
        start_time = time.time()
        while self.recording_30s and (time.time() - start_time) < 30:
            elapsed = int(time.time() - start_time)
            self.recording_status_text.set(f"Recording... {elapsed}s/30s")
            time.sleep(0.5)
        
        if self.recording_30s:  # Jika masih recording (tidak dibatalkan)
            self.recording_30s = False
            self.recording_status_text.set("Processing & Saving...")
            # Schedule plot generation di main thread
            self.window.after(100, self.generate_30s_plots)

    def generate_30s_plots(self):
        """
        Generate dan simpan plots untuk data 30 detik.
        """
        try:
            if not self.recording_data['timestamps']:
                messagebox.showwarning("Warning", "No data recorded!")
                self.recording_status_text.set("Ready")
                return
                
            # Buat direktori output
            output_dir = "saved_signals"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename dengan timestamp
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create figure dengan 4 subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'30-Second Signal Analysis - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                        fontsize=16, fontweight='bold')
            
            # Convert timestamps to seconds from start
            timestamps = np.array(self.recording_data['timestamps'])
            time_sec = timestamps - timestamps[0]
            
            # Plot 1: Raw RGB Signal
            if self.recording_data['raw_rgb']:
                axes[0,0].plot(time_sec[:len(self.recording_data['raw_rgb'])], 
                              self.recording_data['raw_rgb'], 'g-', linewidth=1)
                axes[0,0].set_title('Raw RGB Green Channel Signal', fontweight='bold')
                axes[0,0].set_xlabel('Time (seconds)')
                axes[0,0].set_ylabel('RGB Green Value (0-255)')
                axes[0,0].grid(True, alpha=0.3)
            
            # Plot 2: Filtered rPPG Signal
            if self.recording_data['rppg_filtered']:
                axes[0,1].plot(time_sec[:len(self.recording_data['rppg_filtered'])], 
                              self.recording_data['rppg_filtered'], 'r-', linewidth=1)
                axes[0,1].set_title('Filtered rPPG Signal (Heart Rate)', fontweight='bold')
                axes[0,1].set_xlabel('Time (seconds)')
                axes[0,1].set_ylabel('Normalized Amplitude')
                axes[0,1].grid(True, alpha=0.3)
            
            # Plot 3: Raw Respiration Signal
            if self.recording_data['respirasi_raw']:
                axes[1,0].plot(time_sec[:len(self.recording_data['respirasi_raw'])], 
                              self.recording_data['respirasi_raw'], 'b-', linewidth=1)
                axes[1,0].set_title('Raw Respiration Signal (Shoulder Y-coordinate)', fontweight='bold')
                axes[1,0].set_xlabel('Time (seconds)')
                axes[1,0].set_ylabel('Y Coordinate (normalized)')
                axes[1,0].grid(True, alpha=0.3)
            
            # Plot 4: Filtered Respiration Signal
            if self.recording_data['respirasi_filtered']:
                axes[1,1].plot(time_sec[:len(self.recording_data['respirasi_filtered'])], 
                              self.recording_data['respirasi_filtered'], 'c-', linewidth=1)
                axes[1,1].set_title('Filtered Respiration Signal', fontweight='bold')
                axes[1,1].set_xlabel('Time (seconds)')
                axes[1,1].set_ylabel('Filtered Amplitude')
                axes[1,1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save plot
            plot_filename = os.path.join(output_dir, f"signal_analysis_{now}.png")
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Save raw data
            data_filename = os.path.join(output_dir, f"signal_data_{now}.txt")
            with open(data_filename, 'w') as f:
                f.write(f"# 30-Second Signal Data Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Sampling Rate: {self.fps} Hz\n")
                f.write(f"# Duration: {len(self.recording_data['timestamps'])/self.fps:.1f} seconds\n\n")
                
                # Write data in columns
                f.write("Time(s)\tRaw_RGB\trPPG_Filtered\tRespi_Raw\tRespi_Filtered\n")
                
                max_len = max(len(self.recording_data[key]) for key in self.recording_data if key != 'timestamps')
                
                for i in range(max_len):
                    time_val = time_sec[i] if i < len(time_sec) else ""
                    raw_rgb = self.recording_data['raw_rgb'][i] if i < len(self.recording_data['raw_rgb']) else ""
                    rppg_filt = self.recording_data['rppg_filtered'][i] if i < len(self.recording_data['rppg_filtered']) else ""
                    resp_raw = self.recording_data['respirasi_raw'][i] if i < len(self.recording_data['respirasi_raw']) else ""
                    resp_filt = self.recording_data['respirasi_filtered'][i] if i < len(self.recording_data['respirasi_filtered']) else ""
                    
                    f.write(f"{time_val}\t{raw_rgb}\t{rppg_filt}\t{resp_raw}\t{resp_filt}\n")
            
            success_msg = f"30-second analysis saved:\nPlot: {plot_filename}\nData: {data_filename}"
            messagebox.showinfo("Save Successful", success_msg)
            
        except Exception as e:
            error_msg = f"Failed to generate plots: {str(e)}"
            messagebox.showerror("Plot Error", error_msg)
            print(f"Plot generation error: {traceback.format_exc()}")
        
        finally:
            self.recording_status_text.set("Ready")

    def save_data(self):
        """
        Menyimpan data sinyal yang telah dikumpulkan ke file (existing function).
        """
        if not self.rppg_buffer and not self.respirasi_buffer:
            messagebox.showwarning("No Data", "No signal data to save. Please start monitoring first.")
            return False
            
        try:
            # Buat direktori output jika belum ada
            output_dir = "saved_signals"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename dengan timestamp
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_dir, f"sinyal_log_{now}.txt")
            
            with open(filename, 'w') as f:
                f.write(f"# Signal Data Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Sampling Rate: {self.fps} Hz\n")
                f.write(f"# Buffer Size: rPPG={len(self.rppg_buffer)}, Respirasi={len(self.respirasi_buffer)}\n\n")
                
                f.write("# rPPG Signal (Normalized Green Channel)\n")
                for i, val in enumerate(self.rppg_buffer):
                    f.write(f"{i/self.fps:.3f}\t{val:.6f}\n")
                
                f.write(f"\n# Respirasi Signal (Shoulder Y-coordinate)\n")
                for i, val in enumerate(self.respirasi_buffer):
                    f.write(f"{i/self.fps:.3f}\t{val:.6f}\n")
            
            success_msg = f"Data berhasil disimpan ke:\n{filename}"
            self.video_label.configure(text=success_msg, fg="lime")
            messagebox.showinfo("Save Successful", success_msg)
            return True
            
        except Exception as e:
            error_msg = f"Failed to save data: {str(e)}"
            messagebox.showerror("Save Error", error_msg)
            return False

    def update_video(self):
        """
        Update frame video dan processing sinyal secara real-time.
        Modified untuk menyimpan data selama recording 30 detik.
        """
        if self.running and self.cap:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    raise Exception("Failed to read frame from camera")
                
                # Resize frame untuk processing yang lebih cepat
                frame = cv2.resize(frame, (640, 480))
                display_frame = frame.copy()

                # Ekstraksi dan visualisasi rPPG (landmark dahi)
                raw_rgb_value = None
                try:
                    points = self.rppg_extractor.get_landmarks(frame)
                    for x, y in points:
                        cv2.circle(display_frame, (x, y), 2, (0, 255, 0), -1)

                    bbox = self.rppg_extractor.get_forehead_bbox(frame)
                    if bbox:
                        x1, y1, x2, y2 = bbox
                        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                        cv2.putText(display_frame, "ROI Forehead", (x1, y1 - 5), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                        
                        # Extract raw RGB value untuk recording
                        roi = frame[y1:y2, x1:x2]
                        if roi.size > 0:
                            avg_color = np.mean(roi, axis=(0, 1))  # [B, G, R]
                            raw_rgb_value = avg_color[1]  # Green channel (0-255)
                            
                except Exception as e:
                    print(f"rPPG processing error: {e}")

                # Ekstraksi dan visualisasi respirasi (landmark bahu)
                raw_respirasi_value = None
                try:
                    shoulders = self.respirasi_extractor.get_shoulders(frame)
                    for x, y in shoulders:
                        cv2.circle(display_frame, (x, y), 5, (255, 0, 0), -1)
                        cv2.putText(display_frame, "Shoulder", (x - 30, y + 15), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
                    
                    # Extract raw respirasi value
                    raw_respirasi_value = self.respirasi_extractor.extract(frame)
                    
                except Exception as e:
                    print(f"Respiration processing error: {e}")

                # Ekstraksi sinyal respirasi
                try:
                    y_res = self.respirasi_extractor.extract(frame)
                    if y_res is not None:
                        self.respirasi_buffer.append(y_res)
                        if len(self.respirasi_buffer) > self.buffer_max:
                            self.respirasi_buffer.pop(0)
                except Exception as e:
                    print(f"Respiration extraction error: {e}")

                # Ekstraksi sinyal rPPG
                try:
                    green = self.rppg_extractor.extract(frame)
                    if green is not None:
                        self.rppg_buffer.append(green)
                        if len(self.rppg_buffer) > self.buffer_max:
                            self.rppg_buffer.pop(0)
                except Exception as e:
                    print(f"rPPG extraction error: {e}")

                # Recording 30 detik - simpan data tambahan
                if self.recording_30s:
                    current_time = time.time()
                    self.recording_data['timestamps'].append(current_time)
                    
                    if raw_rgb_value is not None:
                        self.recording_data['raw_rgb'].append(raw_rgb_value)
                    
                    if green is not None:
                        self.recording_data['rppg_filtered'].append(green)
                    
                    if raw_respirasi_value is not None:
                        self.recording_data['respirasi_raw'].append(raw_respirasi_value)
                    
                    # Apply filter pada respirasi raw untuk disimpan juga
                    if len(self.respirasi_buffer) >= 60:
                        try:
                            filtered_resp = apply_bandpass_filter(self.respirasi_buffer, 0.1, 0.5, self.fps)
                            if len(filtered_resp) > 0:
                                self.recording_data['respirasi_filtered'].append(filtered_resp[-1])
                        except:
                            pass

                # Tampilkan frame video
                frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk  # type: ignore[attr-defined]
                self.video_label.configure(image=imgtk)

                # Update grafik
                self.update_hr_plot()
                self.update_rr_plot()

            except Exception as e:
                error_msg = f"Video processing error: {str(e)}"
                print(error_msg)
                self.video_label.configure(text=error_msg, fg="red")
                self.running = False

        # Schedule next update jika masih running
        if self.running:
            self.window.after(33, self.update_video)  # ~30 FPS

    def update_hr_plot(self):
        """
        Update grafik heart rate dengan data sinyal rPPG terbaru.
        
        Menerapkan bandpass filter pada sinyal rPPG dan menghitung heart rate.
        Minimal 60 sample diperlukan untuk filtering yang stabil.
        """
        if len(self.rppg_buffer) < 60:  # Minimal 2 detik data
            return

        try:
            # Apply bandpass filter untuk heart rate (0.7-3.0 Hz = 42-180 BPM)
            filtered = filter_rppg_signal(self.rppg_buffer, self.fps)
            
            # Buat time axis
            x = np.arange(len(filtered)) / self.fps
            
            # Update plot
            self.hr_plot.set_data(x, filtered)
            self.ax_hr.set_xlim(0, x[-1])
            
            # Set y-limits dengan padding untuk visualisasi yang baik
            y_min, y_max = min(filtered), max(filtered)
            y_range = y_max - y_min
            padding = y_range * 0.1 if y_range > 0 else 0.01
            self.ax_hr.set_ylim(y_min - padding, y_max + padding)
            
            # Hitung dan tampilkan heart rate
            bpm = estimate_heart_rate(filtered, self.fps)
            self.ax_hr.set_title(f"{bpm} BPM", color='deeppink', fontsize=12, fontweight='bold')
            
            self.canvas_hr.draw()
            
        except Exception as e:
            print(f"Heart rate plot update error: {e}")

    def update_rr_plot(self):
        """
        Update grafik respiration rate dengan data sinyal respirasi terbaru.
        
        Menerapkan bandpass filter pada sinyal respirasi dan menghitung respiration rate.
        Minimal 60 sample diperlukan untuk filtering yang stabil.
        """
        if len(self.respirasi_buffer) < 60:  # Minimal 2 detik data
            return

        try:
            # Apply bandpass filter untuk respiration rate (0.1-0.5 Hz = 6-30 breaths/min)
            filtered = apply_bandpass_filter(self.respirasi_buffer, 0.1, 0.5, self.fps)
            
            # Buat time axis
            x = np.arange(len(filtered)) / self.fps
            
            # Update plot
            self.rr_plot.set_data(x, filtered)
            self.ax_rr.set_xlim(0, x[-1])
            
            # Set y-limits dengan padding untuk visualisasi yang baik
            y_min, y_max = min(filtered), max(filtered)
            y_range = y_max - y_min
            padding = y_range * 0.1 if y_range > 0 else 0.01
            self.ax_rr.set_ylim(y_min - padding, y_max + padding)
            
            # Hitung dan tampilkan respiration rate
            rr = estimate_respiration_rate(filtered, self.fps)
            self.ax_rr.set_title(f"{rr} Breaths/min", color='cyan', fontsize=12, fontweight='bold')
            
            self.canvas_rr.draw()
            
        except Exception as e:
            print(f"Respiration rate plot update error: {e}")

    def __del__(self):
        """
        Destructor untuk membersihkan resource saat objek dihapus.
        """
        self.cleanup()