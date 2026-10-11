import subprocess


class Effects:
    """ویڈیو پر مختلف effects"""

    EFFECTS = {
        "None": "",
        "Blur": "boxblur=5",
        "Strong Blur": "boxblur=15",
        "Sharpen": "unsharp=5:5:1.0:5:5:0.0",
        "Vignette": "vignette=PI/4",
        "Mirror": "hflip",
        "Flip Vertical": "vflip",
        "Rotate 90": "transpose=1",
        "Rotate 180": "transpose=2,transpose=2",
        "Rotate 270": "transpose=2",
        "Grayscale": "hue=s=0",
        "Invert": "negate",
        "Edge Detect": "edgedetect=low=0.1:high=0.3",
        "Emboss": "convolution='0 1 0:1 -4 1:0 1 0'",
        "Pixelate": "scale=iw/10:ih/10,scale=iw*10:ih*10:flags=neighbor",
        "Posterize": "elbg=codebook_length=8",
        "Old Film": "curves=preset=vintage,noise=alls=15:allf=t",
        "Noise": "noise=alls=20:allf=t+u",
        "Chromatic": "chromashift=cbh=5:crh=-5",
    }

    @staticmethod
    def apply(input_path, output_path, effect="None", intensity=1.0):
        """effect لگائیں"""
        effect_filter = Effects.EFFECTS.get(effect, "")
        if not effect_filter:
            effect_filter = "null"

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", effect_filter,
            "-c:a", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]


class ImageOverlay:
    """ویڈیو پر تصویر / sticker لگائیں"""

    POSITIONS = {
        "اوپر بائیں": "10:10",
        "اوپر دائیں": "W-w-10:10",
        "نیچے بائیں": "10:H-h-10",
        "نیچے دائیں": "W-w-10:H-h-10",
        "درمیان": "(W-w)/2:(H-h)/2",
    }

    @staticmethod
    def overlay(video_path, image_path, output_path,
                position="نیچے دائیں", scale=1.0,
                start=0, end=None, opacity=1.0):
        """تصویر ویڈیو پر لگائیں"""
        pos = ImageOverlay.POSITIONS.get(position, "10:10")

        # scale
        scale_filter = f"scale=iw*{scale}:ih*{scale}" if scale != 1.0 else "null"

        # time enable
        time_filter = ""
        if end is not None and end > start:
            time_filter = f":enable='between(t,{start},{end})'"

        # opacity
        if opacity < 1.0:
            scale_filter += f",format=rgba,colorchannelmixer=aa={opacity}"

        filter_complex = (
            f"[1:v]{scale_filter}[img];"
            f"[0:v][img]overlay={pos}{time_filter}"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", image_path,
            "-filter_complex", filter_complex,
            "-c:a", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]


class KeyframeAnimation:
    """Position/Scale/Opacity کی اینیمیشن"""

    @staticmethod
    def slide_in(video_path, output_path, direction="left", duration=2.0):
        """
        ویڈیو کو سلائیڈ کریں
        direction: left, right, up, down
        """
        # ویڈیو کو اینیمیٹ کرنا: crop یا pad
        # سادہ ورژن: صرف پہلے 2 سیکنڈ میں سلائیڈ
        if direction == "left":
            x_expr = f"if(lt(t\\,{duration})\\,W-(W*t/{duration})\\,0)"
        elif direction == "right":
            x_expr = f"if(lt(t\\,{duration})\\,-(W-(W*t/{duration}))\\,0)"
        elif direction == "up":
            x_expr = f"0:if(lt(t\\,{duration})\\,H-(H*t/{duration})\\,0)"
        elif direction == "down":
            x_expr = f"0:if(lt(t\\,{duration})\\,-(H-(H*t/{duration}))\\,0)"

        # یہ پیچیدہ ہے، سادہ ورژن میں fade استعمال کریں
        return False, "ابھی یہ سادہ ورژن میں دستیاب نہیں"


class AudioMixer:
    """آڈیو کو مکس / volume تبدیل کریں"""

    @staticmethod
    def set_volume(video_path, output_path, volume=1.0):
        """volume 0.0 سے 2.0 تک"""
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-af", f"volume={volume}",
            "-c:v", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]

    @staticmethod
    def mute(video_path, output_path):
        """آواز بند"""
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-an",
            "-c:v", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]

    @staticmethod
    def extract_audio(video_path, output_path):
        """صرف آواز نکالیں"""
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn", "-acodec", "libmp3lame", "-q:a", "2",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]