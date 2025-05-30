# gui.py
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from respirasi_signal import RespirasiExtractor
from rppg_signal import RPPGExtractor
from signal_filter import apply_bandpass_filter
from utils import estimate_heart_rate, estimate_respiration_rate

class RespirasiRPPGApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Realtime rPPG and Respiration Rate Tracker")
        self.window.geometry("1280x720")
        self.window.configure(bg="#2e2e2e")
        self.window.minsize(960, 600)

        self.running = False
        self.cap = None
        self.fps = 30
        self.buffer_max = 300

        self.respirasi_extractor = RespirasiExtractor()
        self.rppg_extractor = RPPGExtractor()

        self.respirasi_buffer = []
        self.rppg_buffer = []

        self.hr_label_text = tk.StringVar(value="-- BPM")
        self.rr_label_text = tk.StringVar(value="-- Breaths/min")

        self.init_layout()

    def run(self):
        self.window.mainloop()

    def init_layout(self):
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=3)
        self.window.columnconfigure(1, weight=2)

        title = tk.Label(self.window, text="Realtime rPPG and Respiration Rate Tracker",
                         font=("Helvetica", 16, "bold"), fg="cyan", bg="#2e2e2e")
        title.grid(row=0, column=0, columnspan=2, pady=10)

        self.video_frame = tk.Frame(self.window, bg="black")
        self.video_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.video_frame.rowconfigure(0, weight=1)
        self.video_frame.columnconfigure(0, weight=1)

        self.video_label = tk.Label(self.video_frame, text="Tekan START untuk memulai feed kamera", fg="white", bg="black")
        self.video_label.grid(sticky="nsew")

        self.right_panel = tk.Frame(self.window, bg="#1e1e1e")
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.rowconfigure(0, weight=1)
        self.right_panel.rowconfigure(1, weight=1)
        self.right_panel.columnconfigure(0, weight=1)

        self.build_hr_plot()
        self.build_rr_plot()

        button_frame = tk.Frame(self.window, bg="#2e2e2e")
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        start_btn = tk.Button(button_frame, text="▶ START", command=self.start_video,
                              bg="lime green", fg="white", font=("Arial", 12, "bold"), width=15)
        start_btn.pack(side=tk.LEFT, padx=20)

        stop_btn = tk.Button(button_frame, text="⏹ STOP", command=self.stop_video,
                             bg="tomato", fg="white", font=("Arial", 12, "bold"), width=15)
        stop_btn.pack(side=tk.LEFT, padx=20)

        save_btn = tk.Button(button_frame, text="💾 SIMPAN", command=self.save_data,
                             bg="dodger blue", fg="white", font=("Arial", 12, "bold"), width=15)
        save_btn.pack(side=tk.LEFT, padx=20)

    def build_hr_plot(self):
        frame = tk.Frame(self.right_panel, bg="#1e1e1e")
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        title = tk.Label(frame, text="❤️ Heart's Rate", fg="deeppink", bg="#1e1e1e", font=("Arial", 12, "bold"))
        title.pack()

        fig, ax = plt.subplots(figsize=(4, 2))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#1e1e1e')
        self.hr_plot, = ax.plot([], [], color='deeppink')
        self.ax_hr = ax
        self.ax_hr.set_title("-- BPM", color='deeppink')
        self.canvas_hr = FigureCanvasTkAgg(fig, master=frame)
        self.canvas_hr.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def build_rr_plot(self):
        frame = tk.Frame(self.right_panel, bg="#1e1e1e")
        frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        title = tk.Label(frame, text="💨 Respiration Rate", fg="cyan", bg="#1e1e1e", font=("Arial", 12, "bold"))
        title.pack()

        fig, ax = plt.subplots(figsize=(4, 2))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#1e1e1e')
        self.rr_plot, = ax.plot([], [], color='cyan')
        self.ax_rr = ax
        self.ax_rr.set_title("-- Breaths/min", color='cyan')
        self.canvas_rr = FigureCanvasTkAgg(fig, master=frame)
        self.canvas_rr.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start_video(self):
        if not self.running:
            self.cap = cv2.VideoCapture(0)
            self.running = True
            self.video_label.configure(text="")
            self.update_video()

    def stop_video(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.configure(image='', text="Feed dihentikan. Tekan START.", fg="white")

    def save_data(self):
        if self.rppg_buffer or self.respirasi_buffer:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sinyal_log_{now}.txt"
            with open(filename, 'w') as f:
                f.write("# rPPG Signal\n")
                for val in self.rppg_buffer:
                    f.write(f"{val:.5f}\n")
                f.write("\n# Respirasi Signal\n")
                for val in self.respirasi_buffer:
                    f.write(f"{val:.5f}\n")
            self.video_label.configure(text="💾 Data disimpan. Tekan START lagi untuk mulai ulang.", fg="white")

    def update_video(self):
        if self.running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                display_frame = frame.copy()

                # Landmark dan bounding box dahi (rPPG)
                points = self.rppg_extractor.get_landmarks(frame)
                for x, y in points:
                    cv2.circle(display_frame, (x, y), 2, (0, 255, 0), -1)

                bbox = self.rppg_extractor.get_forehead_bbox(frame)
                if bbox:
                    x1, y1, x2, y2 = bbox
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    cv2.putText(display_frame, "ROI Forehead", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

                # Landmark bahu (respirasi)
                shoulders = self.respirasi_extractor.get_shoulders(frame)
                for x, y in shoulders:
                    cv2.circle(display_frame, (x, y), 5, (255, 0, 0), -1)
                    cv2.putText(display_frame, "Shoulders", (x, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

                # Ekstraksi sinyal
                y_res = self.respirasi_extractor.extract(frame)
                if y_res is not None:
                    self.respirasi_buffer.append(y_res)
                    if len(self.respirasi_buffer) > self.buffer_max:
                        self.respirasi_buffer.pop(0)

                green = self.rppg_extractor.extract(frame)
                if green is not None:
                    self.rppg_buffer.append(green)
                    if len(self.rppg_buffer) > self.buffer_max:
                        self.rppg_buffer.pop(0)

                frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk  # type: ignore[attr-defined]
                self.video_label.configure(image=imgtk)

                self.update_hr_plot()
                self.update_rr_plot()

        if self.running:
            self.window.after(33, self.update_video)

    def update_hr_plot(self):
        if len(self.rppg_buffer) < 60:
            return
        filtered = apply_bandpass_filter(self.rppg_buffer, 0.7, 3.0, self.fps)
        x = np.arange(len(filtered)) / self.fps
        self.hr_plot.set_data(x, filtered)
        self.ax_hr.set_xlim(0, x[-1])
        self.ax_hr.set_ylim(min(filtered)-0.01, max(filtered)+0.01)
        bpm = estimate_heart_rate(filtered, self.fps)
        self.ax_hr.set_title(f"{bpm} BPM", color='deeppink')
        self.canvas_hr.draw()

    def update_rr_plot(self):
        if len(self.respirasi_buffer) < 60:
            return
        filtered = apply_bandpass_filter(self.respirasi_buffer, 0.1, 0.5, self.fps)
        x = np.arange(len(filtered)) / self.fps
        self.rr_plot.set_data(x, filtered)
        self.ax_rr.set_xlim(0, x[-1])
        self.ax_rr.set_ylim(min(filtered)-0.01, max(filtered)+0.01)
        rr = estimate_respiration_rate(filtered, self.fps)
        self.ax_rr.set_title(f"{rr} Breaths/min", color='cyan')
        self.canvas_rr.draw()
