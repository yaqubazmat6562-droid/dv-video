import subprocess


class AudioDucking:
    """موسیقی کم، آواز زیادہ"""

    @staticmethod
    def duck(video_with_voice, music_path, output_path,
             music_volume=0.3, voice_priority=True):
        """
        ویڈیو کی آواز کو ترجیح دیں
        - music_volume: میوزک کی آواز (0.0 - 1.0)
        """
        # دونوں آڈیو مکس کریں
        # ویڈیو کی آواز فل، میوزک کم
        cmd = [
            "ffmpeg", "-y",
            "-i", video_with_voice,
            "-i", music_path,
            "-filter_complex",
            f"[1:a]volume={music_volume}[music];"
            f"[0:a][music]amix=inputs=2:duration=shortest[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]

    @staticmethod
    def sidechain_duck(video_path, music_path, output_path):
        """
        پروفیسنیل ducking: جب آواز آئے، میوزک دب جائے
        """
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", music_path,
            "-filter_complex",
            "[0:a]asplit=2[voice][sc];"
            "[1:a]volume=0.5[music];"
            "[music][sc]sidechaincompress="
            "threshold=0.05:ratio=8:attack=5:release=300[ducked];"
            "[voice][ducked]amix=inputs=2:duration=shortest[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]