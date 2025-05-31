# rppg_signal.py
import cv2
import numpy as np
import mediapipe as mp

class RPPGExtractor:
    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh( # type: ignore[attr-defined]
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        # Landmark indeks untuk ROI dahi
        self.forehead_indices = [10, 338, 297, 332, 284, 251, 389, 356]

    def extract(self, frame):
        """
        Ekstrak nilai green channel rata-rata dari ROI dahi.
        Ini adalah sinyal rPPG.
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        if not results.multi_face_landmarks:
            return None

        h, w, _ = frame.shape
        lm = results.multi_face_landmarks[0].landmark

        xs, ys = [], []
        for idx in self.forehead_indices:
            x = int(lm[idx].x * w)
            y = int(lm[idx].y * h)
            xs.append(x)
            ys.append(y)

        x_min, x_max = max(min(xs), 0), min(max(xs), w)
        y_min, y_max = max(min(ys), 0), min(max(ys), h)

        roi = frame[y_min:y_max, x_min:x_max]
        if roi.size == 0:
            return None
        avg_color = np.mean(roi, axis=(0, 1))  # [B, G, R]
        return avg_color[1] / 255.0  # Normalisasi green channel

    def get_landmarks(self, frame):
        """
        Mengembalikan koordinat (x, y) dari titik-titik landmark dahi.
        Dipakai untuk visualisasi titik rPPG.
        """
        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0].landmark
            return [(int(lm[idx].x * w), int(lm[idx].y * h)) for idx in self.forehead_indices]
        return []

    def get_forehead_bbox(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        if not results.multi_face_landmarks:
            return None

        h, w, _ = frame.shape
        lm = results.multi_face_landmarks[0].landmark

        # Titik referensi
        center = lm[168]    # antara kedua alis
        top = lm[10]        # titik atas jidat
        left = lm[234]      # sisi kiri dahi
        right = lm[454]     # sisi kanan dahi

        # Atur tinggi ROI hanya sedikit di atas tengah dahi
        roi_top_y = int(center.y * h - 0.10 * h)
        roi_bot_y = int(center.y * h + 0.02 * h)  # sempit agar tidak kena mata
        roi_left_x = int(left.x * w)
        roi_right_x = int(right.x * w)

        # Batasi dalam frame
        x_min = max(0, roi_left_x)
        y_min = max(0, roi_top_y)
        x_max = min(w, roi_right_x)
        y_max = min(h, roi_bot_y)

        return (x_min, y_min, x_max, y_max)
