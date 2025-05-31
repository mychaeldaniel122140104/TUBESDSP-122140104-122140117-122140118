# modules/video_processing.py

import cv2
import time
import numpy as np
from PIL import Image, ImageTk
from tkinter import messagebox

from signal_filter import apply_bandpass_filter
from modules.plotting import update_hr_plot, update_rr_plot


def start_video(app):
    if not app.running:
        try:
            app.cap = cv2.VideoCapture(0)
            if not app.cap.isOpened():
                raise Exception("Cannot access camera. Please check if camera is connected and not used by other applications.")

            app.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            app.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            app.cap.set(cv2.CAP_PROP_FPS, 30)

            app.running = True
            app.video_label.configure(text="")

            app.respirasi_buffer.clear()
            app.rppg_buffer.clear()
            app.raw_rgb_buffer.clear()
            app.respirasi_raw_buffer.clear()

            update_video(app)

        except Exception as e:
            error_msg = f"Failed to start camera: {str(e)}"
            app.video_label.configure(text=error_msg, fg="red", wraplength=400)
            messagebox.showerror("Camera Error", error_msg)
            app.running = False
            if app.cap:
                app.cap.release()
                app.cap = None


def stop_video(app):
    app.running = False
    app.recording_30s = False
    if app.cap:
        app.cap.release()
        app.cap = None
    app.video_label.configure(
        image='',
        text="Feed dihentikan. Tekan START untuk mulai lagi.",
        fg="white"
    )
    app.recording_status_text.set("Ready")


def update_video(app):
    if app.running and app.cap:
        try:
            ret, frame = app.cap.read()
            if not ret:
                raise Exception("Failed to read frame from camera")

            frame = cv2.resize(frame, (640, 480))
            display_frame = frame.copy()

            # rPPG processing
            raw_rgb_value = None
            try:
                points = app.rppg_extractor.get_landmarks(frame)
                for x, y in points:
                    cv2.circle(display_frame, (x, y), 2, (0, 255, 0), -1)

                bbox = app.rppg_extractor.get_forehead_bbox(frame)
                if bbox:
                    x1, y1, x2, y2 = bbox
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    cv2.putText(display_frame, "ROI Forehead", (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

                    roi = frame[y1:y2, x1:x2]
                    if roi.size > 0:
                        avg_color = np.mean(roi, axis=(0, 1))
                        raw_rgb_value = avg_color[1]

            except Exception as e:
                print(f"rPPG processing error: {e}")

            # Respirasi processing
            raw_respirasi_value = None
            try:
                shoulders = app.respirasi_extractor.get_shoulders(frame)
                for x, y in shoulders:
                    cv2.circle(display_frame, (x, y), 5, (255, 0, 0), -1)
                    cv2.putText(display_frame, "Shoulder", (x - 30, y + 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

                raw_respirasi_value = app.respirasi_extractor.extract(frame)

            except Exception as e:
                print(f"Respiration processing error: {e}")

            try:
                y_res = app.respirasi_extractor.extract(frame)
                if y_res is not None:
                    app.respirasi_buffer.append(y_res)
                    if len(app.respirasi_buffer) > app.buffer_max:
                        app.respirasi_buffer.pop(0)
            except Exception as e:
                print(f"Respiration extraction error: {e}")

            try:
                green = app.rppg_extractor.extract(frame)
                if green is not None:
                    app.rppg_buffer.append(green)
                    if len(app.rppg_buffer) > app.buffer_max:
                        app.rppg_buffer.pop(0)
            except Exception as e:
                print(f"rPPG extraction error: {e}")

            if app.recording_30s:
                current_time = time.time()
                app.recording_data['timestamps'].append(current_time)

                if raw_rgb_value is not None:
                    app.recording_data['raw_rgb'].append(raw_rgb_value)

                if green is not None:
                    app.recording_data['rppg_filtered'].append(green)

                if raw_respirasi_value is not None:
                    app.recording_data['respirasi_raw'].append(raw_respirasi_value)

                if len(app.respirasi_buffer) >= 60:
                    try:
                        filtered_resp = apply_bandpass_filter(app.respirasi_buffer, 0.1, 0.5, app.fps)
                        if filtered_resp is not None and len(filtered_resp) > 0:
                            app.recording_data['respirasi_filtered'].append(filtered_resp[-1])
                        else:
                            print("⚠️ Filtered respiration data is empty or None.")
                    except Exception as e:
                        print(f"❌ Error in apply_bandpass_filter: {e}")


            frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            app.video_label.imgtk = imgtk
            app.video_label.configure(image=imgtk)

            update_hr_plot(app)
            update_rr_plot(app)

        except Exception as e:
            error_msg = f"Video processing error: {str(e)}"
            print(error_msg)
            app.video_label.configure(text=error_msg, fg="red")
            app.running = False

    if app.running:
        app.window.after(33, lambda: update_video(app))  # ~30 FPS
