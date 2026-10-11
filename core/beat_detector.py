import subprocess
import struct
import numpy as np


class BeatDetector:
    """آڈیو سے beats نکالیں"""

    @staticmethod
    def detect(video_path, threshold=0.3):
        """beats کے اوقات (سیکنڈ) واپس کریں"""
        # آڈیو نکالیں
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-ac", "1", "-ar", "22050",
            "-f", "s16le", "-"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True)
            raw = result.stdout
        except Exception:
            return []

        if not raw:
            return []

        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
        sr = 22050

        # انرجی نکالیں (ہر 0.05 سیکنڈ پر)
        window = int(sr * 0.05)
        energies = []
        times = []
        for i in range(0, len(samples) - window, window):
            chunk = samples[i:i+window]
            e = np.sum(chunk ** 2) / window
            energies.append(e)
            times.append(i / sr)

        if not energies:
            return []

        energies = np.array(energies)
        max_e = energies.max() if energies.max() > 0 else 1.0

        # Peaks تلاش کریں
        beats = []
        for i in range(1, len(energies) - 1):
            if (energies[i] > energies[i-1] and
                energies[i] > energies[i+1] and
                energies[i] / max_e > threshold):
                beats.append(times[i])

        return beats