import subprocess
import struct
import numpy as np
from PySide6.QtGui import QImage, QColor


class Scopes:
    """ویڈیو کے رنگوں کا تجزیہ"""

    @staticmethod
    def grab_frame(video_path, time=0):
        """ایک فریم نکالیں (PNG bytes)"""
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(time),
            "-i", video_path,
            "-vframes", "1",
            "-f", "image2pipe",
            "-vcodec", "png",
            "-"
        ]
        result = subprocess.run(cmd, capture_output=True)
        return result.stdout if result.returncode == 0 else None

    @staticmethod
    def compute_histogram(png_bytes, bins=256):
        """RGB histogram نکالیں"""
        if not png_bytes:
            return None

        try:
            import io
            from PIL import Image
            img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
            arr = np.array(img)

            r_hist, _ = np.histogram(arr[:, :, 0], bins=bins, range=(0, 255))
            g_hist, _ = np.histogram(arr[:, :, 1], bins=bins, range=(0, 255))
            b_hist, _ = np.histogram(arr[:, :, 2], bins=bins, range=(0, 255))

            return {"r": r_hist, "g": g_hist, "b": b_hist}
        except Exception as e:
            print("Hist error:", e)
            return None