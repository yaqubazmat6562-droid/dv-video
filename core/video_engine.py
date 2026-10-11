import os
import subprocess


class VideoEngine:
    """FFmpeg کے ذریعے ویڈیو پروسیسنگ"""

    @staticmethod
    def trim(input_path, output_path, start, end):
        """ویڈیو کا ایک حصہ کاٹیں (سیکنڈ میں)"""
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ss", str(start),
            "-to", str(end),
            "-c", "copy",
            output_path
        ]
        return VideoEngine._run(cmd)

    @staticmethod
    def change_speed(input_path, output_path, speed=1.0):
        """رفتار تبدیل کریں (1.0 = نارمل، 2.0 = دوگنا، 0.5 = آدھا)"""
        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-filter_complex",
            f"[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={speed}[a]",
            "-map", "[v]", "-map", "[a]",
            output_path
        ]
        return VideoEngine._run(cmd)

    @staticmethod
    def merge(input1, input2, output_path):
        """دو ویڈیوز جوڑیں"""
        cmd = [
            "ffmpeg", "-y",
            "-i", input1,
            "-i", input2,
            "-filter_complex",
            "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
            "-map", "[v]", "-map", "[a]",
            output_path
        ]
        return VideoEngine._run(cmd)

    @staticmethod
    def export(input_path, output_path, resolution="1080p", fps=30):
        """ایکسپورٹ مختلف ریزولوشن میں"""
        scales = {
            "720p": "1280:720",
            "1080p": "1920:1080",
            "4K": "3840:2160"
        }
        scale = scales.get(resolution, "1920:1080")

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", f"scale={scale}",
            "-r", str(fps),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]
        return VideoEngine._run(cmd)

    @staticmethod
    def _run(cmd):
        """کمانڈ چلائیں اور رزلٹ واپس دیں"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            if result.returncode == 0:
                return True, "✅ کامیاب"
            else:
                return False, result.stderr[-500:]  # آخری 500 حروف
        except FileNotFoundError:
            return False, "❌ FFmpeg انسٹال نہیں ہے۔ اسے ڈاؤن لوڈ کر کے PATH میں شامل کریں۔"
        except Exception as e:
            return False, f"❌ {str(e)}"

    @staticmethod
    def export_timeline(clips, output_path, resolution="1080p", fps=30):
        """
        سارے کلپس کو ترتیب سے ملا کر ایک ویڈیو بنائیں
        clips: [{"path": ..., "trim_start": ..., "trim_end": ...}, ...]
        """
        import os
        import subprocess

        if not clips:
            return False, "کوئی کلپ نہیں"

        temp_files = []
        for i, clip in enumerate(clips):
            temp = f"_temp_clip_{i}.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-i", clip["path"],
                "-ss", str(clip.get("trim_start", 0)),
                "-to", str(clip.get("trim_end", 0)),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac",
                temp
            ]
            subprocess.run(cmd, capture_output=True)
            if os.path.exists(temp):
                temp_files.append(temp)

        if not temp_files:
            return False, "کلپس پروسیس نہیں ہو سکے"

        # concat list
        list_file = "_concat_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for t in temp_files:
                f.write(f"file '{os.path.abspath(t)}'\n")

        scales = {"720p": "1280:720", "1080p": "1920:1080", "4K": "3840:2160"}
        scale = scales.get(resolution, "1920:1080")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-vf", f"scale={scale}:force_original_aspect_ratio=decrease,"
                   f"pad={scale}:(ow-iw)/2:(oh-ih)/2",
            "-r", str(fps),
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")

        # صفائی
        for t in temp_files:
            try: os.remove(t)
            except: pass
        try: os.remove(list_file)
        except: pass

        return result.returncode == 0, result.stderr[-500:]        