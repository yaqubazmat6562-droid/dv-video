import os
import json
import time


class AutoSave:
    """خودکار محفوظ"""

    def __init__(self, interval=120, folder=None):
        self.interval = interval  # سیکنڈ
        self.folder = folder or os.path.expanduser("~/DVStudio_autosaves")
        self.last_save = 0
        os.makedirs(self.folder, exist_ok=True)

    def should_save(self):
        return time.time() - self.last_save >= self.interval

    def save(self, data):
        try:
            ts = time.strftime("%Y%m%d_%H%M%S")
            path = os.path.join(self.folder, f"autosave_{ts}.dvproj")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"version": "2.0", "data": data},
                          f, ensure_ascii=False, indent=2)
            self.last_save = time.time()
            self._cleanup()
            return path
        except Exception as e:
            print("AutoSave error:", e)
            return None

    def _cleanup(self, keep=5):
        """صرف آخری 5 آٹو سیو رکھیں"""
        files = sorted(
            [f for f in os.listdir(self.folder) if f.endswith(".dvproj")],
            reverse=True
        )
        for old in files[keep:]:
            try:
                os.remove(os.path.join(self.folder, old))
            except Exception:
                pass