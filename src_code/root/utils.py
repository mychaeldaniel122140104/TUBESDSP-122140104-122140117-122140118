"""
utils.py

Modul ini menyediakan fungsi untuk mengestimasi detak jantung (heart rate) dan laju pernapasan (respiration rate)
dari sinyal fisiologis menggunakan analisis spektrum daya (power spectral density) melalui metode periodogram.

Fungsi:
- estimate_heart_rate(signal, fs): Menghitung detak jantung (dalam bpm) berdasarkan sinyal rPPG.
- estimate_respiration_rate(signal, fs): Menghitung laju pernapasan (dalam bpm) berdasarkan sinyal respirasi.
"""

import numpy as np  # Untuk operasi numerik
from scipy.signal import periodogram  # Untuk menghitung periodogram sinyal


def estimate_heart_rate(signal, fs):
    """
    Mengestimasi detak jantung (heart rate) dari sinyal rPPG menggunakan analisis spektrum daya.

    Args:
        signal (array-like): Sinyal input, biasanya rPPG (photoplethysmogram).
        fs (float): Frekuensi sampling sinyal dalam Hz.

    Returns:
        int: Detak jantung dalam beats per minute (bpm). Jika tidak ada puncak dominan, mengembalikan 0.
    """
    # Hitung spektrum daya (power spectral density) dari sinyal
    f, Pxx = periodogram(signal, fs)

    # Batasi ke rentang frekuensi detak jantung normal (0.7–3.0 Hz = 42–180 bpm)
    f_range = (f >= 0.7) & (f <= 3.0)

    # Jika tidak ada komponen frekuensi dalam rentang tersebut, kembalikan 0
    if not np.any(f_range):
        return 0

    # Cari frekuensi dominan (frekuensi dengan energi tertinggi) dalam rentang tersebut
    peak_freq = f[f_range][np.argmax(Pxx[f_range])]

    # Konversi frekuensi dari Hz ke bpm
    return int(peak_freq * 60)


def estimate_respiration_rate(signal, fs):
    """
    Mengestimasi laju pernapasan (respiration rate) dari sinyal respirasi menggunakan analisis spektrum daya.

    Args:
        signal (array-like): Sinyal input, misalnya pergerakan bahu atau dada.
        fs (float): Frekuensi sampling sinyal dalam Hz.

    Returns:
        int: Laju pernapasan dalam breaths per minute (bpm). Jika tidak ada puncak dominan, mengembalikan 0.
    """
    # Hitung spektrum daya dari sinyal
    f, Pxx = periodogram(signal, fs)

    # Batasi ke rentang frekuensi napas normal (0.1–0.5 Hz = 6–30 bpm)
    f_range = (f >= 0.1) & (f <= 0.5)

    # Jika tidak ada komponen frekuensi dalam rentang tersebut, kembalikan 0
    if not np.any(f_range):
        return 0

    # Cari frekuensi dominan dalam rentang tersebut
    peak_freq = f[f_range][np.argmax(Pxx[f_range])]

    # Konversi frekuensi dari Hz ke bpm
    return int(peak_freq * 60)
