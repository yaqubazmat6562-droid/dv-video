import json
import os


class ProjectIO:
    @staticmethod
    def save(data, output_path):
        """data: dict یا list دونوں سپورٹ"""
        if isinstance(data, list):
            data = {"video_track": data,
                    "video_track_2": [],
                    "video_track_3": []}
        payload = {"version": "2.0", "data": data}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return True

    @staticmethod
    def load(path):
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        # نیا فارمیٹ
        if "data" in payload:
            return payload["data"]
        # پرانا فارمیٹ
        return payload.get("clips", None)