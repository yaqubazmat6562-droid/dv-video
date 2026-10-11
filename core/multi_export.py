import subprocess
import os
from concurrent.futures import ThreadPoolExecutor


class MultiExport:
    """کئی ورژن ایک ساتھ ایکسپورٹ کریں"""

    @staticmethod
    def export_versions(input_path, output_dir, base_name,
                        versions=None):
        """
        versions = [
            {"resolution": "720p", "fps": 30, "suffix": "_720p30"},
            {"resolution": "1080p", "fps": 60, "suffix": "_1080p60"},
            {"resolution": "4K", "fps": 30, "suffix": "_4k"},
        ]
        """
        if versions is None:
            versions = [
                {"resolution": "720p", "fps": 30, "suffix": "_720p"},
                {"resolution": "1080p", "fps": 30, "suffix": "_1080p"},
            ]

        os.makedirs(output_dir, exist_ok=True)
        results = []

        def _do(ver):
            output = os.path.join(
                output_dir, f"{base_name}{ver['suffix']}.mp4"
            )
            scales = {"720p": "1280:720", "1080p": "1920:1080",
                      "4K": "3840:2160"}
            scale = scales.get(ver["resolution"], "1920:1080")

            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-vf", f"scale={scale}:force_original_aspect_ratio=decrease,"
                       f"pad={scale}:(ow-iw)/2:(oh-ih)/2",
                "-r", str(ver["fps"]),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                output
            ]
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="ignore")
            return (ver["suffix"], r.returncode == 0, output)

        # متوازی ایکسپورٹ (زیادہ سے زیادہ 3 بیک وقت)
        with ThreadPoolExecutor(max_workers=3) as ex:
            results = list(ex.map(_do, versions))

        return results


class ProxyGenerator:
    """کم ریزولوشن پروکسی بنائیں"""

    @staticmethod
    def generate(input_path, output_path, scale=0.5):
        """پروکسی فائل (1/2 یا 1/4 ریزولوشن)"""
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", f"scale=iw*{scale}:ih*{scale}",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-c:a", "aac", "-b:a", "96k",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]