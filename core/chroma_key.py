import subprocess


class ChromaKey:
    """Green/Blue screen سے بیک گراؤنڈ ہٹائیں"""

    COLORS = {
        "سبز (Green)": "0x00FF00",
        "نیلا (Blue)": "0x0000FF",
        "سرخ (Red)": "0xFF0000",
    }

    @staticmethod
    def remove_background(video_path, output_path,
                          bg_video_or_image=None,
                          color="سبز (Green)",
                          similarity=0.3,
                          blend=0.1):
        """
        بیک گراؤنڈ ہٹائیں
        - bg_video_or_image: نئی بیک گراؤنڈ (اختیاری)
        - similarity: رنگ کی مشابہت (0.1 - 0.5)
        - blend: کناروں کی نرمی (0.0 - 0.3)
        """
        key_color = ChromaKey.COLORS.get(color, "0x00FF00")

        if bg_video_or_image is None:
            # صرف شفاف (webm)
            filter_complex = (
                f"[0:v]chromakey={key_color}:{similarity}:{blend},"
                f"format=yuva420p[out]"
            )
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
                output_path
            ]
        else:
            # نئی بیک گراؤنڈ لگائیں
            filter_complex = (
                f"[0:v]chromakey={key_color}:{similarity}:{blend}[fg];"
                f"[1:v]scale=1920:1080[bg];"
                f"[bg][fg]overlay=shortest=1[out]"
            )
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", bg_video_or_image,
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-c:a", "copy",
                output_path
            ]

        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding="utf-8", errors="ignore")
        return result.returncode == 0, result.stderr[-500:]