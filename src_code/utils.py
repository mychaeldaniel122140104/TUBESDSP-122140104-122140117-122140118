# utils.py
import numpy as np
from scipy.signal import periodogram

def estimate_heart_rate(signal, fs):
    f, Pxx = periodogram(signal, fs)
    f_range = (f >= 0.7) & (f <= 3.0)
    if not np.any(f_range): return 0
    peak_freq = f[f_range][np.argmax(Pxx[f_range])]
    return int(peak_freq * 60)

def estimate_respiration_rate(signal, fs):
    f, Pxx = periodogram(signal, fs)
    f_range = (f >= 0.1) & (f <= 0.5)
    if not np.any(f_range): return 0
    peak_freq = f[f_range][np.argmax(Pxx[f_range])]
    return int(peak_freq * 60)
