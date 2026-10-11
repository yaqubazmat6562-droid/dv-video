import subprocess


class LUTLoader:
    """Cinema LUT (.cube) لگائیں"""

    @staticmethod
    def apply(input_path, output_path, lut_path, intensity=1.0):
        """
        LUT فائل ویڈیو پر لگائیں
        - intensity: 0.0 - 1.0 (1.0 = مکمل)
        """
        # FFmpeg lut3d فلٹر
        lut_escaped = lut_path.replace("\\", "/").replace(":", "\\:")

        if intensity < 1.0:
            # mix اصل اور LUT والی
            vf = (
                f"split[a][b];"
                f"[a]lut3d='{lut_escaped}'[lut];"
                f"[lut][b]blend=all_mode=normal:all_opacity={intensity}"
            )
        else:
            vf = f"lut3d='{lut_escaped}'"

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


class ColorWheels:
    """Lift / Gamma / Gain color correction"""

    @staticmethod
    def apply(input_path, output_path,
              lift_r=0.0, lift_g=0.0, lift_b=0.0,
              gamma_r=1.0, gamma_g=1.0, gamma_b=1.0,
              gain_r=1.0, gain_g=1.0, gain_b=1.0):
        """رنگوں کی درست کاری"""
        vf = (
            f"colorbalance="
            f"rs={lift_r}:gs={lift_g}:bs={lift_b}:"
            f"rm={gamma_r - 1.0}:gm={gamma_g - 1.0}:bm={gamma_b - 1.0}:"
            f"rh={gain_r - 1.0}:gh={gain_g - 1.0}:bh={gain_b - 1.0}"
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