# modules/plotting.py
# Fungsi-fungsi untuk membangun dan memperbarui grafik heart rate dan respiratory rate.
# plotting artinya membuat grafik untuk menampilkan data heart rate dan respiratory rate secara real-time.
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

# Import modul-modul yang diperlukan
from signal_filter import apply_bandpass_filter, filter_rppg_signal
from utils import estimate_heart_rate, estimate_respiration_rate


# Fungsi untuk membangun plot pada antarmuka pengguna
# build_plot membangun plot untuk heart rate dan respiratory rate pada antarmuka pengguna.
# Fungsi ini membuat frame, label, dan plot menggunakan Matplotlib,
def build_plot(app, parent, row, title, color, attr_plot, attr_ax, attr_canvas, title_suffix):
    '''Membangun plot untuk heart rate atau respiratory rate pada antarmuka pengguna.
    Membuat frame, label, dan plot menggunakan Matplotlib.
      Parameters:
        app : objek utama aplikasi yang menyimpan state
        parent : frame parent untuk meletakkan plot
        row : posisi baris di grid layout
        title : judul label grafik
        color : warna garis plot dan teks
        attr_plot, attr_ax, attr_canvas : nama atribut yang akan disimpan di app
        title_suffix : satuan seperti BPM atau Breaths/min
    '''
    frame = tk.Frame(parent, bg="#1e1e1e")
    frame.grid(row=row, column=0, sticky="nsew", padx=10, pady=10)
    #
    label = tk.Label(frame, text=title, fg=color, bg="#1e1e1e", font=("Arial", 12, "bold"))
    label.pack()

    fig, ax = plt.subplots(figsize=(4, 2))
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

    # Inisialisasi plot
    line, = ax.plot([], [], color=color, linewidth=2)
    ax.set_title(f"-- {title_suffix}", color=color, fontsize=12, fontweight='bold')
    ax.set_xlabel("Time (s)", color='white')
    ax.set_ylabel("Amplitude", color='white')
    
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Simpan objek plotting ke atribut app
    setattr(app, attr_plot, line)
    setattr(app, attr_ax, ax)
    setattr(app, attr_canvas, canvas)


def update_plot(app, buffer, filter_func, fps, plot_line, ax, canvas, label_suffix, title_color):
    """ Memperbarui plot dengan data sinyal yang telah difilter.
    Fungsi ini memfilter sinyal, memperbarui data plot, dan menghitung estimasi heart rate atau respiratory rate.
    Parameters yang digunakan:
        buffer : data sinyal mentah
        filter_func : fungsi untuk memfilter sinyal
        fps : frame per second (sampling rate)
        plot_line : objek line matplotlib
        ax : objek axis matplotlib
        canvas : canvas untuk menggambar ulang
        label_suffix : satuan teks (BPM, Breaths/min)
        title_color : warna teks judul plot
    """
    
    if not buffer or len(buffer) < 60 or plot_line is None or ax is None or canvas is None:
        return

    try:
        # Filter sinyal dan perbarui plot
        filtered = filter_func(buffer, fps)
        x = np.arange(len(filtered)) / fps
        # Update data pada plot
        plot_line.set_data(x, filtered)
        ax.set_xlim(0, x[-1])
        # Set y-axis limits with padding
        y_min, y_max = min(filtered), max(filtered)
        y_range = y_max - y_min
        # Tambahkan padding 10% dari rentang y jika rentang positif, atau 0.01 jika tidak
        padding = y_range * 0.1 if y_range > 0 else 0.01
        ax.set_ylim(y_min - padding, y_max + padding)

        # Hitung heart rate atau respiratory rate
        rate = estimate_heart_rate(filtered, fps) if label_suffix == 'BPM' \
            else estimate_respiration_rate(filtered, fps)

        ax.set_title(f"{rate} {label_suffix}", color=title_color, fontsize=12, fontweight='bold')
        canvas.draw()

    # Handle exceptions during plot update
    except Exception as e:
        print(f"Plot update error ({label_suffix}): {e}")


def update_hr_plot(app):
    """ Memperbarui plot heart rate dengan data rPPG yang telah difilter.
    Fungsi ini memfilter sinyal rPPG, memperbarui data plot, dan menghitung estimasi heart rate.
    """
    update_plot(
        app=app,
        buffer=app.rppg_buffer,
        filter_func=filter_rppg_signal,
        fps=app.fps,
        plot_line=app.hr_plot,
        ax=app.ax_hr,
        canvas=app.canvas_hr,
        label_suffix='BPM',
        title_color='deeppink'
    )


def update_rr_plot(app):
    """ Memperbarui plot respiratory rate dengan data respirasi yang telah difilter.
    Fungsi ini memfilter sinyal respirasi, memperbarui data plot, dan menghitung estimasi respiratory rate.
    """
    update_plot(
        app=app,
        buffer=app.respirasi_buffer,
        filter_func=lambda buf, fs: apply_bandpass_filter(buf, 0.1, 0.5, fs),
        fps=app.fps,
        plot_line=app.rr_plot,
        ax=app.ax_rr,
        canvas=app.canvas_rr,
        label_suffix='Breaths/min',
        title_color='cyan'
    )


def _plot_signal_subplot(ax, time_sec, data, color, title, ylabel):
    """ Membuat subplot untuk menampilkan sinyal dengan waktu dan data yang diberikan.
    """
    if data:
        ax.plot(time_sec[:len(data)], data, color, linewidth=1)
        ax.set_title(title, fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
