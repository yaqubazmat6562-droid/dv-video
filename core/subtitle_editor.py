import os


class SubtitleEditor:
    """دستی SRT بنائیں/پڑھیں"""

    @staticmethod
    def parse_srt(path):
        """SRT فائل پڑھیں"""
        if not os.path.exists(path):
            return []
        subs = []
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        blocks = content.strip().split("\n\n")
        for block in blocks:
            lines = block.split("\n")
            if len(lines) < 3:
                continue
            try:
                idx = int(lines[0])
                times = lines[1].split(" --> ")
                start = SubtitleEditor._to_sec(times[0])
                end = SubtitleEditor._to_sec(times[1])
                text = "\n".join(lines[2:])
                subs.append({"index": idx, "start": start,
                             "end": end, "text": text})
            except Exception:
                continue
        return subs

    @staticmethod
    def save_srt(subs, path):
        """SRT محفوظ کریں"""
        def fmt(t):
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = int(t % 60)
            ms = int((t - int(t)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        with open(path, "w", encoding="utf-8") as f:
            for i, s in enumerate(subs, 1):
                f.write(f"{i}\n")
                f.write(f"{fmt(s['start'])} --> {fmt(s['end'])}\n")
                f.write(f"{s['text'].strip()}\n\n")
        return path

    @staticmethod
    def _to_sec(t_str):
        """HH:MM:SS,mmm → seconds"""
        t_str = t_str.strip().replace(",", ".")
        parts = t_str.split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        return 0