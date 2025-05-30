# signal_filter.py
from scipy.signal import butter, filtfilt

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_bandpass_filter(data, lowcut, highcut, fs, order=5):
    padlen = 3 * order
    if len(data) <= padlen:
        return data  # Belum cukup data untuk difilter, kembalikan asli
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    return filtfilt(b, a, data)
    