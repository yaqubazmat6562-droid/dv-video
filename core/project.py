class Project:
    def __init__(self):
        self.name = "Untitled"
        self.clips = []       # List of dicts
        self.current_video = None

    def add_clip(self, path):
        self.clips.append({
            "path": path,
            "trim_start": 0,
            "trim_end": None,
            "speed": 1.0,
        })

    def set_current(self, path):
        self.current_video = path