import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import threading
import numpy as np
from respiration import extract_respiration_signal, apply_bandpass_filter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SignalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pemantauan Sinyal Vital - Respirasi & rPPG")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1a1a1a")  # tema gelap

        self.signal_data = []
        self.max_signal_length = 150  # batas data grafik

        self.running = False
        self.cap = None
        self.frames = []

        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.root, text="Sistem Pemantauan Sinyal Vital", font=("Helvetica", 18), bg="#1a1a1a", fg="white")
        title.pack(pady=10)

        # Area Webcam
        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(pady=10)

        # Tombol Kontrol
        button_frame = tk.Frame(self.root, bg="#1a1a1a")
        button_frame.pack(pady=10)

        start_button = ttk.Button(button_frame, text="Start", command=self.start_camera)
        start_button.grid(row=0, column=0, padx=10)

        stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_camera)
        stop_button.grid(row=0, column=1, padx=10)

        process_button = ttk.Button(button_frame, text="Proses Sinyal", command=self.process_signal)
        process_button.grid(row=0, column=2, padx=10)

        self.status_label = tk.Label(self.root, text="Status: Siap", font=("Helvetica", 12), bg="#1a1a1a", fg="lightgreen")
        self.status_label.pack(pady=5)

        # Area Grafik
        plot_frame = tk.Frame(self.root, bg="#1a1a1a")
        plot_frame.pack(pady=10)

        self.fig, self.ax = plt.subplots(figsize=(6, 2), dpi=100)
        self.ax.set_facecolor("black")
        self.ax.set_title("Sinyal Respirasi", color='white')
        self.ax.set_xlabel("Frame", color='white')
        self.ax.set_ylabel("Intensitas", color='white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')

        self.line, = self.ax.plot([], [], color='cyan')

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack()

    def start_camera(self):
        if not self.running:
            self.running = True
            self.frames = []
            self.cap = cv2.VideoCapture(0)
            threading.Thread(target=self.update_frame).start()
            self.status_label.config(text="Status: Kamera Aktif", fg="lightgreen")

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.video_label.config(image='')
        self.status_label.config(text="Status: Kamera Berhenti", fg="orange")

    def update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            self.frames.append(frame)

            # Tampilkan frame ke GUI
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

            # Ambil ROI dan channel hijau
            roi = frame[100:200, 100:200, 1]  # ROI (Y1:Y2, X1:X2, channel hijau)
            mean_intensity = np.mean(roi)
            self.signal_data.append(mean_intensity)
            if len(self.signal_data) > self.max_signal_length:
                self.signal_data.pop(0)

            # Update grafik real-time
            self.line.set_data(range(len(self.signal_data)), self.signal_data)
            self.ax.set_xlim(0, self.max_signal_length)
            self.ax.set_ylim(min(self.signal_data, default=0)-5, max(self.signal_data, default=1)+5)
            self.canvas.draw()

    def process_signal(self):
        if len(self.frames) < 30:
            self.status_label.config(text="Status: Frame tidak cukup!", fg="red")
            return

        self.status_label.config(text="Status: Memproses sinyal...", fg="yellow")

        roi = (100, 100, 200, 200)  # ROI: x1, y1, x2, y2
        raw_signal = extract_respiration_signal(self.frames, roi=roi)
        filtered_signal = apply_bandpass_filter(raw_signal)

        # Tampilkan sinyal hasil filter
        self.ax.clear()
        self.ax.set_facecolor("black")
        self.ax.plot(filtered_signal, color='cyan')
        self.ax.set_title("Sinyal Respirasi (Terfilter)", color='white')
        self.ax.set_xlabel("Frame", color='white')
        self.ax.set_ylabel("Intensitas", color='white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')

        self.canvas.draw()

        self.status_label.config(text="Status: Sinyal diproses", fg="lightgreen")

    def on_close(self):
        self.stop_camera()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SignalApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
