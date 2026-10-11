import os
import subprocess


class TextOverlay:
    """FFmpeg کے ذریعے ویڈیو پر ٹیکسٹ لگائیں"""

    # رنگوں کے نام (FFmpeg format)
    COLORS = {
        "سفید": "white",
        "کالا": "black",
        "سرخ": "red",
        "نیلا": "blue",
        "سبز": "green",
        "پیلا": "yellow",
        "گلابی": "pink",
        "جامنی": "purple",
        "نارنجی": "orange",
        "سنہری": "gold",
    }

    # پوزیشنز
    POSITIONS = {
        "اوپر": "(w-text_w)/2:h*0.05",
        "درمیان": "(w-text_w)/2:(h-text_h)/2",
        "نیچے": "(w-text_w)/2:h-text_h-h*0.05",
        "بائیں اوپر": "w*0.05:h*0.05",
        "دائیں اوپر": "w-text_w-w*0.05:h*0.05",
        "بائیں نیچے": "w*0.05:h-text_h-h*0.05",
        "دائیں نیچے": "w-text_w-w*0.05:h-text_h-h*0.05",
    }

    @staticmethod
    def add_text(video_path, output_path, text,
                 position="نیچے", color="سفید",
                 font_size=48, start=0, end=None,
                 font_file=None, bg_box=False):
        """
        ویڈیو پر ٹیکسٹ شامل کریں
        - position: پوزیشن (POSITIONS میں سے)
        - color: رنگ (COLORS میں سے)
        - font_size: سائز
        - start/end: کب سے کب تک (سیکنڈ میں)
        - bg_box: ٹیکسٹ کے پیچھے سیاہ باکس
        """
        color_ff = TextOverlay.COLORS.get(color, "white")
        pos_ff = TextOverlay.POSITIONS.get(position, "(w-text_w)/2:h-text_h-40")

        # فونٹ فائل
        if font_file is None:
            # Windows کا ڈیفالٹ فونٹ (Arial)
            win_font = "C:/Windows/Fonts/arial.ttf"
            if os.path.exists(win_font):
                font_file = win_font.replace(":", "\\:").replace("/", "/")
            else:
                font_file = ""

        # ٹیکسٹ escape کریں
        text_safe = text.replace("'", "\\'").replace(":", "\\:")

        # فونٹ فلٹر
        font_part = f":fontfile='{font_file}'" if font_file else ""
        box_part = ":box=1:boxcolor=black@0.6:boxborderw=10" if bg_box else ""

        # وقت کی شرط
        time_part = ""
        if end is not None and end > start:
            time_part = f":enable='between(t,{start},{end})'"

        vf = (
            f"drawtext=text='{text_safe}'"
            f"{font_part}"
            f":fontcolor={color_ff}"
            f":fontsize={font_size}"
            f":x={pos_ff.split(':')[0]}"
            f":y={pos_ff.split(':')[1]}"
            f"{box_part}"
            f"{time_part}"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", vf,
            "-c:a", "copy",
            output_path
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="ignore"
        )
        return result.returncode == 0, result.stderr[-500:]