import os
import subprocess


class CaptionGenerator:
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.model = None

    def load_model(self):
        try:
            import whisper
            print(f"📥 Loading Whisper: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            print("✅ Model loaded")
            return True
        except ImportError:
            print("❌ Whisper انسٹال نہیں")
            return False
        except Exception as e:
            print(f"❌ {e}")
            return False

    def transcribe(self, video_path):
        if self.model is None:
            if not self.load_model():
                return None

        audio_path = os.path.splitext(video_path)[0] + "_audio.wav"
        self._extract_audio(video_path, audio_path)

        if not os.path.exists(audio_path):
            return None

        print("🎙 Transcribing...")
        result = self.model.transcribe(audio_path)

        try:
            os.remove(audio_path)
        except Exception:
            pass

        return result

    def _extract_audio(self, video_path, audio_path):
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            audio_path
        ]
        subprocess.run(cmd, capture_output=True)

    def save_srt(self, segments, output_path):
        def fmt(t):
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = int(t % 60)
            ms = int((t - int(t)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        with open(output_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments, 1):
                f.write(f"{i}\n")
                f.write(f"{fmt(seg['start'])} --> {fmt(seg['end'])}\n")
                f.write(f"{seg['text'].strip()}\n\n")

        return output_path

    def burn_subtitles(self, video_path, srt_path, output_path):
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", f"subtitles='{srt_escaped}'",
            "-c:a", "copy",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]