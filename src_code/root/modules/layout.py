# modules/layout.py

# Membuat antarmuka pengguna untuk aplikasi pelacakan rPPG dan laju pernapasan secara real-time
import tkinter as tk
import tkinter.messagebox as messagebox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from modules.video_processing import start_video, stop_video
from modules.recording import start_30s_recording, save_data
from modules.plotting import build_plot

def init_layout(app):
    """
    Inisialisasi layout dan komponen GUI dengan tombol recording tambahan.
    Membangun antarmuka pengguna untuk aplikasi pelacakan rPPG dan laju pernapasan secara real-time.
    """
    # Konfigurasi grid layout
    app.window.rowconfigure(1, weight=1)
    app.window.columnconfigure(0, weight=3) # Panel video kiri 
    app.window.columnconfigure(1, weight=2) # Panel video kanan

    # Title 
    title = tk.Label(app.window, text="Pemantauan Sinyal rPPG dan Respiration Rate Secara Real-Time",
                     font=("Helvetica", 16, "bold"), fg="cyan", bg="#2e2e2e")
    title.grid(row=0, column=0, columnspan=2, pady=10)

    # Video frame
    app.video_frame = tk.Frame(app.window, bg="black")
    app.video_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    app.video_frame.rowconfigure(0, weight=1)
    app.video_frame.columnconfigure(0, weight=1)
    # Label untuk menampilkan feed video
    app.video_label = tk.Label(app.video_frame, 
                              text="Tekan START untuk memulai feed kamera", 
                              fg="white", bg="black")
    app.video_label.grid(sticky="nsew")
    # Label untuk menampilkan status video
    # Panel kanan untuk grafik
    app.right_panel = tk.Frame(app.window, bg="#1e1e1e")
    app.right_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
    app.right_panel.rowconfigure(0, weight=1)
    app.right_panel.rowconfigure(1, weight=1)
    app.right_panel.rowconfigure(2, weight=0)  # Status recording
    app.right_panel.columnconfigure(0, weight=1)

    # Build plots
    build_plot(app, app.right_panel, 0, "❤️ Heart Rate", "deeppink", "hr_plot", "ax_hr", "canvas_hr", "BPM")
    build_plot(app, app.right_panel, 1, "💨 Respiration Rate", "cyan", "rr_plot", "ax_rr", "canvas_rr", "Breaths/min")

    # Recording status
    app.recording_status_label = tk.Label(app.right_panel, 
                                         textvariable=app.recording_status_text,
                                         fg="yellow", bg="#1e1e1e", 
                                         font=("Arial", 10, "bold"))
    app.recording_status_label.grid(row=2, column=0, pady=5)

    # Tombol kontrol
    button_frame = tk.Frame(app.window, bg="#2e2e2e")
    button_frame.grid(row=2, column=0, columnspan=2, pady=10)
    # Tombol kontrol untuk memulai, menghentikan, merekam, dan menyimpan data
    start_btn = tk.Button(button_frame, text="▶ START", command=lambda: start_video(app),
                          bg="lime green", fg="white", font=("Arial", 12, "bold"), width=12)
    start_btn.pack(side=tk.LEFT, padx=10)

    stop_btn = tk.Button(button_frame, text="⏹ STOP", command=lambda: stop_video(app),
                         bg="tomato", fg="white", font=("Arial", 12, "bold"), width=12)
    stop_btn.pack(side=tk.LEFT, padx=10)

    record_btn = tk.Button(button_frame, text="📊 RECORD 30s", command=lambda: start_30s_recording(app),
                           bg="orange", fg="white", font=("Arial", 12, "bold"), width=15)
    record_btn.pack(side=tk.LEFT, padx=10)

    save_btn = tk.Button(button_frame, text="💾 SIMPAN", command=lambda: save_data(app),
                         bg="dodger blue", fg="white", font=("Arial", 12, "bold"), width=12)
    save_btn.pack(side=tk.LEFT, padx=10)
