import os
import subprocess
import struct
from PySide6.QtGui import QImage, QPainter, QColor, QPen
from PySide6.QtCore import Qt


class WaveformGenerator:
    """FFmpeg سے آڈیو waveform نکالیں"""

    @staticmethod
    def extract_peaks(video_path, num_samples=500):
        """آڈیو سے peaks نکالیں (0.0 - 1.0)"""
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-ac", "1",
            "-ar", "8000",
            "-f", "s16le",
            "-"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True)
            raw = result.stdout
        except Exception:
            return []

        if not raw:
            return []

        # ہر 2 bytes = ایک sample (s16le)
        samples = []
        for i in range(0, len(raw) - 1, 2):
            val = struct.unpack("<h", raw[i:i+2])[0]
            samples.append(abs(val))

        if not samples:
            return []

        # نمونے کم کریں
        chunk = max(1, len(samples) // num_samples)
        peaks = []
        for i in range(0, len(samples), chunk):
            group = samples[i:i+chunk]
            if group:
                peaks.append(max(group) / 32768.0)   # normalize

        return peaks

    @staticmethod
    def draw_waveform(painter, width, height, peaks, color="#4caf50"):
        """QPainter سے waveform بنائیں"""
        if not peaks:
            return

        pen = QPen(QColor(color))
        pen.setWidth(1)
        painter.setPen(pen)

        mid = height // 2
        step = width / len(peaks)

        for i, peak in enumerate(peaks):
            x = int(i * step)
            h = int(peak * mid * 0.9)
            painter.drawLine(x, mid - h, x, mid + h)