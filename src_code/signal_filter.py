# signal_filter.py
"""
Modul untuk filtering sinyal digital menggunakan Butterworth bandpass filter.

Modul ini menyediakan fungsi untuk menerapkan bandpass filter pada sinyal
rPPG dan respirasi untuk menghilangkan noise dan mengekstrak frekuensi
yang relevan untuk heart rate dan respiration rate.

Author: [Nama Tim]
Date: [Tanggal]
"""

from scipy.signal import butter, filtfilt, medfilt, savgol_filter
import numpy as np
import warnings


def butter_bandpass(lowcut, highcut, fs, order=5):
    """
    Membuat koefisien filter Butterworth bandpass.
    
    Filter Butterworth dipilih karena:
    1. Memiliki flat frequency response di passband
    2. Tidak memiliki ripple seperti Chebyshev filter
    3. Memberikan transisi yang smooth antara passband dan stopband
    4. Cocok untuk aplikasi biomedical signal processing
    
    Args:
        lowcut (float): Frekuensi cutoff bawah dalam Hz
        highcut (float): Frekuensi cutoff atas dalam Hz  
        fs (float): Sampling frequency dalam Hz
        order (int): Order filter (default=5, memberikan rolloff -30dB/decade)
        
    Returns:
        tuple: Koefisien filter (b, a) untuk scipy.signal.filtfilt
        
    Raises:
        ValueError: Jika parameter frekuensi tidak valid
    """
    # Validasi parameter
    if lowcut <= 0 or highcut <= 0:
        raise ValueError("Cutoff frequencies must be positive")
    if lowcut >= highcut:
        raise ValueError("Low cutoff must be less than high cutoff")
    if fs <= 0:
        raise ValueError("Sampling frequency must be positive")
    if highcut >= fs/2:
        raise ValueError("High cutoff must be less than Nyquist frequency")
    
    # Nyquist frequency (setengah dari sampling rate)
    nyq = 0.5 * fs
    
    # Normalisasi frekuensi cutoff terhadap Nyquist frequency
    low = lowcut / nyq
    high = highcut / nyq
    
    # Desain filter Butterworth bandpass
    b, a = butter(order, [low, high], btype='band')
    return b, a


def apply_bandpass_filter(data, lowcut, highcut, fs, order=5):
    """
    Menerapkan bandpass filter pada sinyal menggunakan zero-phase filtering.
    
    Fungsi ini menggunakan filtfilt (forward-backward filtering) untuk:
    1. Menghilangkan phase distortion
    2. Memberikan effective order 2x lipat (2*order)
    3. Mempertahankan bentuk gelombang asli sinyal
    
    PARAMETER JUSTIFICATION:
    
    Untuk sinyal rPPG (Heart Rate):
    - Lowcut: 0.7 Hz (42 BPM) - Batas bawah normal heart rate orang dewasa
    - Highcut: 3.0 Hz (180 BPM) - Batas atas heart rate maksimal
    - Alasan: Menghilangkan DC component dan high frequency noise
             dari pergerakan, pencahayaan, dan electrical interference
    
    Untuk sinyal Respirasi:
    - Lowcut: 0.1 Hz (6 breaths/min) - Batas bawah normal breathing rate
    - Highcut: 0.5 Hz (30 breaths/min) - Batas atas breathing rate maksimal
    - Alasan: Isolasi sinyal pernapasan dari gerakan tubuh lain dan noise
    
    Order 5 dipilih karena:
    - Memberikan rolloff -30dB/decade yang cukup tajam
    - Tidak terlalu tinggi sehingga menghindari numerical instability
    - Cocok untuk real-time processing dengan delay minimal
    
    Args:
        data (list or numpy.array): Data sinyal input
        lowcut (float): Frekuensi cutoff bawah dalam Hz
        highcut (float): Frekuensi cutoff atas dalam Hz
        fs (float): Sampling frequency dalam Hz
        order (int): Order filter Butterworth (default=5)
        
    Returns:
        numpy.array: Sinyal yang telah difilter
        
    Raises:
        ValueError: Jika parameter tidak valid atau data terlalu pendek
    """
    # Konversi ke numpy array jika diperlukan
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    
    # Minimum length untuk filtfilt: 3 * max(len(a), len(b))
    # Untuk Butterworth order 5: coefficient length = 6
    # Minimum padlen untuk filtfilt: 3 * order = 15
    padlen = 3 * order
    
    if len(data) <= padlen:
        print(f"Warning: Data length ({len(data)}) too short for filtering (need >{padlen}). Returning original data.")
        return data
    
    try:
        # Dapatkan koefisien filter
        b, a = butter_bandpass(lowcut, highcut, fs, order)
        
        # Apply zero-phase filtering
        # filtfilt menerapkan filter dua kali (forward + backward)
        # sehingga menghilangkan phase delay dan memberikan effective order 2*order
        filtered_data = filtfilt(b, a, data)
        
        return filtered_data
        
    except Exception as e:
        print(f"Filtering error: {e}. Returning original data.")
        return data


def apply_median_filter(data, kernel_size=5):
    """
    Menerapkan median filter untuk menghilangkan spike noise.
    
    Median filter efektif untuk:
    1. Menghilangkan impulse noise dan outliers
    2. Mempertahankan edge/transisi tajam dalam sinyal
    3. Non-linear filtering yang robust terhadap extreme values
    
    Args:
        data (array-like): Data sinyal input
        kernel_size (int): Ukuran kernel median filter (harus ganjil)
        
    Returns:
        numpy.array: Sinyal yang telah difilter
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    
    if len(data) < kernel_size:
        print(f"Warning: Data too short for median filtering. Returning original data.")
        return data
    
    # Pastikan kernel_size ganjil
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    try:
        filtered_data = medfilt(data, kernel_size=kernel_size)
        return filtered_data
    except Exception as e:
        print(f"Median filtering error: {e}. Returning original data.")
        return data


def apply_savgol_filter(data, window_length=11, poly_order=3):
    """
    Menerapkan Savitzky-Golay filter untuk smoothing sinyal.
    
    Savitzky-Golay filter berguna untuk:
    1. Smoothing noise sambil mempertahankan bentuk sinyal
    2. Preservasi fitur seperti peaks dan valleys
    3. Tidak menggeser phase sinyal
    
    Args:
        data (array-like): Data sinyal input
        window_length (int): Panjang window (harus ganjil dan > poly_order)
        poly_order (int): Order polynomial fitting (biasanya 2-4)
        
    Returns:
        numpy.array: Sinyal yang telah difilter
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    
    if len(data) < window_length:
        print(f"Warning: Data too short for Savgol filtering. Returning original data.")
        return data
    
    # Pastikan window_length ganjil dan > poly_order
    if window_length % 2 == 0:
        window_length += 1
    if window_length <= poly_order:
        window_length = poly_order + 2
        if window_length % 2 == 0:
            window_length += 1
    
    try:
        filtered_data = savgol_filter(data, window_length, poly_order)
        return filtered_data
    except Exception as e:
        print(f"Savgol filtering error: {e}. Returning original data.")
        return data


def preprocess_signal(data, fs, signal_type="rPPG", apply_median=True, apply_savgol=True):
    """
    Preprocessing lengkap untuk sinyal rPPG atau respirasi.
    
    Pipeline preprocessing:
    1. Median filter - menghilangkan spike noise
    2. Savitzky-Golay filter - smoothing
    3. Bandpass filter - ekstraksi frekuensi target
    
    Args:
        data (array-like): Data sinyal input
        fs (float): Sampling frequency dalam Hz
        signal_type (str): "rPPG" atau "respirasi"
        apply_median (bool): Apakah menggunakan median filter
        apply_savgol (bool): Apakah menggunakan Savitzky-Golay filter
        
    Returns:
        numpy.array: Sinyal yang telah dipreprocess
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    
    if len(data) < 30:  # Minimal 1 detik data pada 30 FPS
        print(f"Warning: Data too short for preprocessing. Returning original data.")
        return data
    
    processed_data = data.copy()
    
    try:
        # Step 1: Median filter untuk menghilangkan outliers
        if apply_median:
            processed_data = apply_median_filter(processed_data, kernel_size=5)
        
        # Step 2: Savitzky-Golay filter untuk smoothing
        if apply_savgol:
            window_len = min(11, len(processed_data) // 3)
            if window_len % 2 == 0:
                window_len -= 1
            if window_len >= 5:
                processed_data = apply_savgol_filter(processed_data, 
                                                   window_length=window_len, 
                                                   poly_order=3)
        
        # Step 3: Bandpass filter berdasarkan jenis sinyal
        if signal_type.lower() == "rppg":
            # Heart rate range: 42-180 BPM (0.7-3.0 Hz)
            processed_data = apply_bandpass_filter(processed_data, 0.7, 3.0, fs)
        elif signal_type.lower() == "respirasi":
            # Respiration rate range: 6-30 breaths/min (0.1-0.5 Hz)
            processed_data = apply_bandpass_filter(processed_data, 0.1, 0.5, fs)
        else:
            print(f"Warning: Unknown signal type '{signal_type}'. Skipping bandpass filter.")
        
        return processed_data
        
    except Exception as e:
        print(f"Preprocessing error: {e}. Returning original data.")
        return data


def validate_signal_quality(data, fs, signal_type="unknown"):
    """
    Validasi kualitas sinyal sebelum filtering.
    
    Fungsi ini melakukan basic quality check pada sinyal untuk
    memastikan sinyal layak untuk diproses lebih lanjut.
    
    Args:
        data (array-like): Data sinyal
        fs (float): Sampling frequency
        signal_type (str): Jenis sinyal ("rPPG" atau "respirasi")
        
    Returns:
        dict: Dictionary berisi hasil validasi dan metrics
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    
    result = {
        "valid": True,
        "messages": [],
        "metrics": {}
    }
    
    # Check data length
    min_duration = 2.0  # minimum 2 detik data
    min_samples = int(min_duration * fs)
    if len(data) < min_samples:
        result["valid"] = False
        result["messages"].append(f"Data too short: {len(data)} samples, need at least {min_samples}")
    
    # Check for NaN or infinite values
    nan_count = np.sum(np.isnan(data))
    inf_count = np.sum(np.isinf(data))
    if nan_count > 0 or inf_count > 0:
        result["valid"] = False
        result["messages"].append(f"Invalid values: {nan_count} NaN, {inf_count} infinite")
    
    # Check signal variance (tidak boleh terlalu flat)
    signal_var = np.var(data)
    if signal_var < 1e-10:
        result["valid"] = False
        result["messages"].append(f"Signal too flat: variance = {signal_var:.2e}")
    
    # Check dynamic range
    signal_range = np.max(data) - np.min(data)
    if signal_range < 1e-6:
        result["valid"] = False
        result["messages"].append(f"Signal dynamic range too small: {signal_range:.2e}")
    
    # Calculate quality metrics
    result["metrics"] = {
        "length": len(data),
        "duration_sec": len(data) / fs,
        "mean": np.mean(data),
        "std": np.std(data),
        "variance": signal_var,
        "min": np.min(data),
        "max": np.max(data),
        "range": signal_range,
        "nan_count": nan_count,
        "inf_count": inf_count
    }
    
    # Signal-specific validation
    if signal_type.lower() == "rppg":
        # rPPG signal should be normalized between 0-1
        if np.min(data) < -0.1 or np.max(data) > 1.1:
            result["messages"].append("rPPG signal outside expected range [0, 1]")
            
    elif signal_type.lower() == "respirasi":
        # Respirasi signal should show periodic variation
        # Check if signal has reasonable amplitude variation
        if signal_range < 0.01:  # Very small range for breathing motion
            result["messages"].append("Respiration signal amplitude too small")
    
    if not result["valid"]:
        result["messages"].insert(0, "Signal quality validation FAILED:")
    else:
        result["messages"].append("Signal quality validation PASSED")
    
    return result


def adaptive_filter_params(data, fs, signal_type="rPPG"):
    """
    Menentukan parameter filter yang optimal berdasarkan karakteristik sinyal.
    
    Args:
        data (array-like): Data sinyal
        fs (float): Sampling frequency
        signal_type (str): Jenis sinyal ("rPPG" atau "respirasi")
        
    Returns:
        dict: Parameter filter yang direkomendasikan
    """
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    
    # Default parameters
    params = {
        "lowcut": 0.7 if signal_type.lower() == "rppg" else 0.1,
        "highcut": 3.0 if signal_type.lower() == "rppg" else 0.5,
        "order": 5,
        "median_kernel": 5,
        "savgol_window": 11,
        "savgol_poly": 3
    }
    
    # Adaptive adjustments based on signal characteristics
    signal_std = np.std(data)
    signal_length = len(data)
    
    # Adjust filter order based on data length and noise level
    if signal_length < 100:
        params["order"] = 3  # Lower order for short signals
    elif signal_std > 0.1:  # High noise
        params["order"] = 6  # Higher order for noisy signals
    
    # Adjust median filter kernel based on noise level
    if signal_std > 0.05:
        params["median_kernel"] = 7  # Larger kernel for noisy signals
    elif signal_std < 0.01:
        params["median_kernel"] = 3  # Smaller kernel for clean signals
    
    # Adjust Savgol window based on signal length
    max_window = min(21, signal_length // 5)
    if max_window < 5:
        max_window = 5
    if max_window % 2 == 0:
        max_window -= 1
    params["savgol_window"] = min(params["savgol_window"], max_window)
    
    return params


# Convenience functions untuk GUI
def filter_rppg_signal(data, fs=30):
    """
    Convenience function untuk filtering sinyal rPPG.
    Digunakan langsung oleh GUI untuk heart rate processing.
    """
    return preprocess_signal(data, fs, signal_type="rPPG")


def filter_respiration_signal(data, fs=30):
    """
    Convenience function untuk filtering sinyal respirasi.
    Digunakan langsung oleh GUI untuk respiration rate processing.
    """
    return preprocess_signal(data, fs, signal_type="respirasi")


# Backward compatibility - fungsi yang sudah ada di GUI tetap berfungsi
# apply_bandpass_filter sudah didefinisikan di atas dan kompatibel dengan GUI