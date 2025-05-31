"""
Modul untuk filtering sinyal digital menggunakan Butterworth bandpass filter.

Digunakan untuk preprocessing sinyal rPPG dan respirasi:
- Median filter
- Savitzky-Golay filter
- Bandpass Butterworth

Author: [Nama Tim]
"""

from scipy.signal import butter, filtfilt, medfilt, savgol_filter
import numpy as np
import warnings


def butter_bandpass(lowcut, highcut, fs, order=5):
    if lowcut <= 0 or highcut <= 0:
        raise ValueError("Cutoff frequencies must be positive")
    if lowcut >= highcut:
        raise ValueError("Low cutoff must be less than high cutoff")
    if fs <= 0:
        raise ValueError("Sampling frequency must be positive")
    if highcut >= fs / 2:
        raise ValueError("High cutoff must be less than Nyquist frequency")

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    try:
        result = butter(order, [low, high], btype='band')
        if result is None:
            raise ValueError("❌ scipy.signal.butter() returned None")
        if not isinstance(result, tuple) or len(result) != 2:
            raise ValueError(f"❌ Unexpected butter() output: {result}")
        return result  # b, a
    except Exception as e:
        print(f"❌ Error in butter_bandpass(): {e}")
        return None




def apply_bandpass_filter(data, lowcut, highcut, fs, order=5):
    if data is None or len(data) < order * 2:
        raise ValueError("Data is None or too short for filtering")

    try:
        result = butter_bandpass(lowcut, highcut, fs, order)
        if result is None:
            raise ValueError("butter_bandpass() returned None")
        b, a = result
        filtered_data = filtfilt(b, a, data)
        return filtered_data
    except Exception as e:
        print(f"Filtering error: {e}. Returning original data.")
        return np.array(data)


def apply_median_filter(data, kernel_size=5):
    if not isinstance(data, np.ndarray):
        data = np.array(data)

    if len(data) < kernel_size:
        print("Warning: Data too short for median filtering. Returning original data.")
        return data

    if kernel_size % 2 == 0:
        kernel_size += 1

    try:
        return medfilt(data, kernel_size=kernel_size)
    except Exception as e:
        print(f"Median filtering error: {e}. Returning original data.")
        return data


def apply_savgol_filter(data, window_length=11, poly_order=3):
    if not isinstance(data, np.ndarray):
        data = np.array(data)

    if len(data) < window_length:
        print("Warning: Data too short for Savgol filtering. Returning original data.")
        return data

    if window_length % 2 == 0:
        window_length += 1
    if window_length <= poly_order:
        window_length = poly_order + 2
        if window_length % 2 == 0:
            window_length += 1

    try:
        return savgol_filter(data, window_length, poly_order)
    except Exception as e:
        print(f"Savgol filtering error: {e}. Returning original data.")
        return data


def preprocess_signal(data, fs, signal_type="rPPG", apply_median=True, apply_savgol=True):
    if not isinstance(data, np.ndarray):
        data = np.array(data)

    if data is None or len(data) < 30:
        print("Warning: Data too short for preprocessing. Returning original data.")
        return data

    processed_data = data.copy()

    try:
        if apply_median:
            processed_data = apply_median_filter(processed_data, kernel_size=5)

        if apply_savgol:
            window_len = max(5, min(11, len(processed_data) // 3))
            if window_len % 2 == 0:
                window_len -= 1
            if window_len >= 5:
                processed_data = apply_savgol_filter(processed_data,
                                                     window_length=window_len,
                                                     poly_order=3)

        if signal_type.lower() == "rppg":
            processed_data = apply_bandpass_filter(processed_data, 0.7, 3.0, fs)
        elif signal_type.lower() == "respirasi":
            processed_data = apply_bandpass_filter(processed_data, 0.1, 0.5, fs)
        else:
            print(f"Warning: Unknown signal type '{signal_type}'. Skipping bandpass filter.")

        return processed_data

    except Exception as e:
        print(f"Preprocessing error: {e}. Returning original data.")
        return data


# === Convenience functions untuk GUI ===

def filter_rppg_signal(data, fs=30):
    return preprocess_signal(data, fs, signal_type="rPPG")


def filter_respiration_signal(data, fs=30):
    return preprocess_signal(data, fs, signal_type="respirasi")
