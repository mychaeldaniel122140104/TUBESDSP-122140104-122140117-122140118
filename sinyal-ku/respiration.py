import numpy as np
from scipy.signal import butter, filtfilt
import cv2

def extract_respiration_signal(frames, roi=None):
    # Ambil area ROI dari setiap frame dan hitung rata-rata brightness hijau
    x1, y1, x2, y2 = roi
    signal = []

    for frame in frames:
        roi_frame = frame[y1:y2, x1:x2]
        green_channel = roi_frame[:, :, 1]  # channel hijau
        mean_value = np.mean(green_channel)
        signal.append(mean_value)

    return np.array(signal)

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_bandpass_filter(data, lowcut=0.1, highcut=0.5, fs=30, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    y = filtfilt(b, a, data, axis=0)
    return y

def extract_respiratory_signal(frames):
    intensity_values = []

    for frame in frames:
        gray = np.mean(frame, axis=2)  # konversi ke grayscale
        roi = gray[200:300, 270:370]   # contoh ROI di tengah (tweak sesuai wajah)
        intensity = np.mean(roi)
        intensity_values.append(intensity)

    raw_signal = np.array(intensity_values)
    filtered_signal = apply_bandpass_filter(raw_signal)
    return filtered_signal