import copy


class ProjectManager:
    """Undo/Redo + Split کا انتظام"""

    def __init__(self):
        self.history = []       # ساری اسٹیٹس
        self.redo_stack = []
        self.max_history = 50

    def save_state(self, state):
        """موجودہ حالت محفوظ کریں"""
        self.history.append(copy.deepcopy(state))
        if len(self.history) > self.max_history:
            self.history.pop(0)
        self.redo_stack.clear()

    def undo(self, current_state):
        """ایک قدم پیچھے"""
        if len(self.history) < 2:
            return None
        # موجودہ حالت redo میں ڈالیں
        self.redo_stack.append(copy.deepcopy(current_state))
        self.history.pop()  # موجودہ
        return self.history[-1]   # پچھلی حالت

    def redo(self, current_state):
        """ایک قدم آگے"""
        if not self.redo_stack:
            return None
        self.history.append(copy.deepcopy(current_state))
        return self.redo_stack.pop()

    def can_undo(self):
        return len(self.history) > 1

    def can_redo(self):
        return len(self.redo_stack) > 0


class ClipOperations:
    """کلپس پر آپریشنز"""

    @staticmethod
    def split_clip(clip_data, at_time):
        """
        کلپ کو at_time (سیکنڈ) پر دو حصوں میں بانٹیں
        clip_data: {path, duration, trim_start, trim_end}
        returns: (left_clip, right_clip) یا None
        """
        trim_start = clip_data.get("trim_start", 0)
        trim_end = clip_data.get("trim_end", clip_data.get("duration", 0))

        # at_time اصل ویڈیو ٹائم لائن میں ہے
        if at_time <= trim_start or at_time >= trim_end:
            return None

        left = {
            "path": clip_data["path"],
            "duration": clip_data["duration"],
            "trim_start": trim_start,
            "trim_end": at_time,
        }
        right = {
            "path": clip_data["path"],
            "duration": clip_data["duration"],
            "trim_start": at_time,
            "trim_end": trim_end,
        }
        return left, right