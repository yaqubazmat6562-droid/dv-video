import subprocess
import os


class AIStyle:
    """AI style transfer + filters"""

    # Style presets (FFmpeg filters کی شکل میں)
    STYLES = {
        "Anime": "curves=preset=strong_contrast,eq=saturation=1.6:contrast=1.2,"
                 "unsharp=5:5:1.5",
        "Oil Painting": "convolution='0 -1 0:-1 5 -1:0 -1 0',"
                        "eq=saturation=1.3",
        "Sketch": "edgedetect=low=0.05:high=0.2,negate,eq=contrast=1.5",
        "Watercolor": "boxblur=2,eq=saturation=1.4:brightness=0.1",
        "Neon": "chromashift=cbh=10:crh=-10,eq=saturation=2.0:contrast=1.3",
        "Cyberpunk": "colorbalance=rs=0.3:bs=0.4:gm=-0.1,"
                     "eq=saturation=1.5:contrast=1.2",
        "Matrix": "colorchannelmixer=.3:.4:.3:0:.3:.9:.3:0:.3:.4:.3,"
                  "eq=contrast=1.4",
        "Dream": "gblur=sigma=3,eq=brightness=0.1:saturation=1.2",
        "VHS": "curves=vintage,noise=alls=30:allf=t+u,"
               "eq=saturation=1.4",
        "Noir": "hue=s=0,eq=contrast=1.4:brightness=-0.05",
    }

    @staticmethod
    def apply_style(input_path, output_path, style="Anime"):
        filter_str = AIStyle.STYLES.get(style, "null")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", filter_str,
            "-c:a", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]