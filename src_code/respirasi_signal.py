# respirasi_signal.py
import cv2
from mediapipe import solutions as mp_solutions


class RespirasiExtractor:
    def __init__(self):
        self.mp_pose = mp_solutions.pose # type: ignore[attr-defined]
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def extract(self, frame):
        """
        Mengembalikan nilai Y (vertikal) rata-rata dari bahu kiri dan kanan.
        Dipakai sebagai sinyal respirasi.
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            left = lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right = lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            return (left.y + right.y) / 2
        return None

    def get_shoulders(self, frame):
        """
        Mengembalikan koordinat (x, y) bahu kiri dan kanan dalam satuan piksel.
        Dipakai untuk visualisasi landmark respirasi.
        """
        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            return [
                (int(lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x * w),
                 int(lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y * h)),
                (int(lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w),
                 int(lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h))
            ]
        return []
