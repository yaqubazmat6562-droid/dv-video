import subprocess
import json


class MotionTracker:
    """OpenCV سے آبجیکٹ ٹریک کریں"""

    @staticmethod
    def track_object(video_path, start_time=0, duration=5.0):
        """
        سادہ optical flow tracking
        returns: [(frame_idx, x, y), ...] points
        """
        try:
            import cv2
            import numpy as np
        except ImportError:
            return []

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)

        # پہلا فریم
        ret, old_frame = cap.read()
        if not ret:
            return []

        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

        # خودکار feature points (corners)
        p0 = cv2.goodFeaturesToTrack(
            old_gray, maxCorners=100, qualityLevel=0.3,
            minDistance=7, blockSize=7
        )
        if p0 is None:
            return []

        points = []
        max_frames = int(duration * fps)
        frame_idx = 0

        while frame_idx < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Lucas-Kanade optical flow
            p1, st, err = cv2.calcOpticalFlowPyrLK(
                old_gray, frame_gray, p0, None
            )

            if p1 is None:
                break

            # اچھی points چنیں
            good_new = p1[st == 1]
            good_old = p0[st == 1]

            if len(good_new) > 0:
                # اوسط حرکت
                avg_x = float(good_new[:, 0].mean())
                avg_y = float(good_new[:, 1].mean())
                points.append({
                    "frame": frame_idx,
                    "time": start_time + frame_idx / fps,
                    "x": avg_x,
                    "y": avg_y,
                })

            old_gray = frame_gray.copy()
            p0 = good_new.reshape(-1, 1, 2)
            frame_idx += 1

        cap.release()
        return points

    @staticmethod
    def apply_stabilization(input_path, output_path):
        """ویڈیو stabilization (vidstab)"""
        # پہلا pass
        cmd1 = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", "vidstabdetect=shakiness=5:accuracy=15",
            "-f", "null", "-"
        ]
        subprocess.run(cmd1, capture_output=True)

        # دوسرا pass
        cmd2 = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", "vidstabtransform=smoothing=10:zoom=0",
            "-c:a", "copy",
            output_path
        ]
        result = subprocess.run(cmd2, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]