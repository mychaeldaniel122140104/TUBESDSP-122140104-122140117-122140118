import cv2
import numpy as np
from scipy.signal import butter, filtfilt
from respiration import extract_respiratory_signal
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_bandpass_filter(data, lowcut=0.7, highcut=4.0, fs=30, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    y = filtfilt(b, a, data, axis=0)
    return y

def extract_rppg_signal(frames):
    green_values = []

    for frame in frames:
        # Ambil saluran hijau (Green Channel)
        green = frame[:, :, 1]
        green_mean = np.mean(green)
        green_values.append(green_mean)

    # Convert ke numpy array
    signal = np.array(green_values)
    filtered_signal = apply_bandpass_filter(signal)

    return filtered_signal

def capture_frames(duration=10, fps=30):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Webcam tidak ditemukan")

    frames = []
    total_frames = duration * fps
    print(f"Merekam selama {duration} detik...")

    while len(frames) < total_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        frames.append(frame)
        cv2.imshow("Webcam - Rekaman", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return frames

if __name__ == "__main__":
    # Ambil video dari webcam
    frames = capture_frames()

    # Ekstraksi sinyal rPPG
    rppg_signal = extract_rppg_signal(frames)

    # Ekstraksi sinyal respirasi
    respiration_signal = extract_respiratory_signal(frames)

    # Visualisasi keduanya
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(rppg_signal, color='g')
    plt.title("Sinyal rPPG (Green Channel - Filtered)")
    plt.xlabel("Frame")
    plt.ylabel("Intensitas")

    plt.subplot(2, 1, 2)
    plt.plot(respiration_signal, color='b')
    plt.title("Sinyal Respirasi (ROI Grayscale - Filtered)")
    plt.xlabel("Frame")
    plt.ylabel("Intensitas")

    plt.tight_layout()
    plt.show()
