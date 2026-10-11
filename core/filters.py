import subprocess


class VideoFilters:
    """ویڈیو پر مختلف فلٹرز لگائیں"""

    # رنگوں کی preset فہرست
    PRESETS = {
        "None": "",
        "Warm": "colorbalance=rs=0.3:gs=0.1:bs=-0.1",
        "Cool": "colorbalance=rs=-0.1:gs=0.1:bs=0.3",
        "Vintage": "curves=vintage",
        "B&W": "hue=s=0",
        "Sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
        "Vivid": "eq=saturation=1.5:contrast=1.1",
        "Fade": "curves=color_neg",
        "Dramatic": "eq=contrast=1.4:brightness=-0.05:saturation=0.8",
        "Cinematic": "colorbalance=rs=0.1:gs=0.0:bs=0.2,eq=contrast=1.15",
    }

    @staticmethod
    def apply_filter(input_path, output_path, preset="None",
                     brightness=0.0, contrast=1.0, saturation=1.0):
        """فلٹر لگائیں"""
        filters = []

        # preset
        preset_filter = VideoFilters.PRESETS.get(preset, "")
        if preset_filter:
            filters.append(preset_filter)

        # manual adjustments
        if brightness != 0.0 or contrast != 1.0 or saturation != 1.0:
            filters.append(
                f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}"
            )

        if not filters:
            # کوئی تبدیلی نہیں
            filters.append("null")

        vf = ",".join(filters)

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", vf,
            "-c:a", "copy",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]


class Transitions:
    """کلپس کے درمیان transitions"""

    @staticmethod
    def fade_in_out(input_path, output_path, fade_in=1.0, fade_out=1.0):
        """آغاز اور اختتام پر fade"""
        # ویڈیو کی لمبائی معلوم کریں
        import json
        try:
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", input_path
            ], capture_output=True, text=True)
            duration = float(json.loads(result.stdout)["format"]["duration"])
        except Exception:
            duration = 5.0

        fade_out_start = max(0, duration - fade_out)

        vf = (
            f"fade=t=in:st=0:d={fade_in},"
            f"fade=t=out:st={fade_out_start}:d={fade_out}"
        )
        af = (
            f"afade=t=in:st=0:d={fade_in},"
            f"afade=t=out:st={fade_out_start}:d={fade_out}"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", vf,
            "-af", af,
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]


class ZoomPan:
    """تصویر یا ویڈیو پر زوم / پین (Ken Burns effect)"""

    @staticmethod
    def apply_zoom(input_path, output_path, zoom_start=1.0,
                   zoom_end=1.5, duration=None):
        """آہستہ آہستہ زوم"""
        import json
        try:
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", input_path
            ], capture_output=True, text=True)
            dur = float(json.loads(result.stdout)["format"]["duration"])
        except Exception:
            dur = duration or 5.0

        # zoompan filter: زوم آہستہ آہستہ بڑھے
        # z='min(zoom+0.0015,1.5)'
        z_expr = f"'{zoom_start}+({zoom_end}-{zoom_start})*on/{int(dur*25)}'"

        vf = (
            f"zoompan=z={z_expr}:d={int(dur*25)}:s=1920x1080:fps=25"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", vf,
            "-c:a", "copy",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]


class SpeedRamp:
    """کلپ کے اندر رفتار تبدیل کریں"""

    @staticmethod
    def apply(input_path, output_path, segments):
        """
        segments = [
            {"start": 0, "end": 2, "speed": 1.0},
            {"start": 2, "end": 4, "speed": 2.0},
            {"start": 4, "end": 6, "speed": 0.5},
        ]
        """
        # سادہ ورژن: پوری ویڈیو پر ایک speed
        # (اصل speed ramping کے لیے پیچیدہ filter_complex چاہیے)
        if len(segments) == 1:
            speed = segments[0]["speed"]
            vf = f"setpts={1/speed}*PTS"
            af = f"atempo={speed}"

            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-vf", vf,
                "-af", af,
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    encoding="utf-8", errors="ignore")
            return result.returncode == 0, result.stderr[-500:]

        return False, "Multi-segment speed ramp ابھی سپورٹ نہیں"