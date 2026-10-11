class Markers:
    """Timeline مارکرز"""

    def __init__(self):
        self.markers = []   # [{"time": 5.0, "color": "#ff3b3b", "label": "Beat"}]

    def add(self, time, color="#ff3b3b", label=""):
        self.markers.append({"time": time, "color": color, "label": label})
        self.markers.sort(key=lambda m: m["time"])

    def remove_at(self, time, tolerance=0.1):
        self.markers = [m for m in self.markers
                        if abs(m["time"] - time) > tolerance]

    def get_all(self):
        return self.markers

    def clear(self):
        self.markers.clear()