# utils.py
# Import library yang dibutuhkan
import numpy as np  # Untuk operasi numerik
from scipy.signal import periodogram  # Untuk menghitung periodogram sinyal

# Fungsi untuk mengestimasi detak jantung (heart rate) dari sinyal
def estimate_heart_rate(signal, fs):
    # Hitung spektrum daya (power spectral density) dari sinyal
    f, Pxx = periodogram(signal, fs)
    
    # Batasi frekuensi ke rentang detak jantung normal (0.7–3.0 Hz atau sekitar 42–180 bpm)
    f_range = (f >= 0.7) & (f <= 3.0)
    
    # Jika tidak ada frekuensi dalam rentang tersebut, kembalikan 0
    if not np.any(f_range): return 0
    
    # Cari frekuensi dengan puncak tertinggi (dominant frequency) dalam rentang yang dipilih
    peak_freq = f[f_range][np.argmax(Pxx[f_range])]
    
    # Konversi dari Hz ke bpm (beats per minute) dengan mengalikan 60
    return int(peak_freq * 60)

# Fungsi untuk mengestimasi laju pernapasan (respiration rate) dari sinyal
def estimate_respiration_rate(signal, fs):
    # Hitung spektrum daya dari sinyal
    f, Pxx = periodogram(signal, fs)
    
    # Batasi frekuensi ke rentang napas normal (0.1–0.5 Hz atau sekitar 6–30 bpm)
    f_range = (f >= 0.1) & (f <= 0.5)
    
    # Jika tidak ada frekuensi dalam rentang tersebut, kembalikan 0
    if not np.any(f_range): return 0
    
    # Cari frekuensi dominan dalam rentang tersebut
    peak_freq = f[f_range][np.argmax(Pxx[f_range])]
    
    # Konversi ke breaths per minute dengan mengalikan 60
    return int(peak_freq * 60)
