import subprocess


class GPUEncoder:
    """GPU ایکسپورٹ کے لیے"""

    @staticmethod
    def detect_gpu():
        """پتہ لگائیں کہ کون سا GPU encoder دستیاب ہے"""
        encoders = {
            "nvenc": "h264_nvenc",      # NVIDIA
            "qsv": "h264_qsv",          # Intel
            "amf": "h264_amf",          # AMD
            "cpu": "libx264",            # CPU fallback
        }
        available = []
        try:
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True, text=True, timeout=5
            )
            for key, enc in encoders.items():
                if enc in result.stdout:
                    available.append(key)
        except Exception:
            available = ["cpu"]

        return available

    @staticmethod
    def get_best_encoder():
        """بہترین encoder منتخب کریں"""
        available = GPUEncoder.detect_gpu()
        for pref in ["nvenc", "qsv", "amf", "cpu"]:
            if pref in available:
                return pref
        return "cpu"

    @staticmethod
    def get_encoder_args(encoder="auto", quality="medium"):
        """FFmpeg encoder args"""
        if encoder == "auto":
            encoder = GPUEncoder.get_best_encoder()

        args_map = {
            "nvenc": ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "23"],
            "qsv": ["-c:v", "h264_qsv", "-preset", "medium", "-global_quality", "23"],
            "amf": ["-c:v", "h264_amf", "-quality", "balanced", "-rc", "cqp"],
            "cpu": ["-c:v", "libx264", "-preset", quality, "-crf", "23"],
        }
        return args_map.get(encoder, args_map["cpu"])