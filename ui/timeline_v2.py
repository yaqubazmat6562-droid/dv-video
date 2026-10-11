import os
import json
import subprocess
import copy
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QMenu, QSlider, QPushButton,
    QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

from core.project_manager import ProjectManager, ClipOperations


# ==================== Clip Widget ====================
class ClipWidget(QFrame):
    clicked = Signal(object)
    deleted = Signal(object)
    moved = Signal(object, int)
    resized = Signal(object, int, int)
    split_requested = Signal(object, float)
    duplicate_requested = Signal(object)
    copy_requested = Signal(object)

    HANDLE_WIDTH = 8

    def __init__(self, clip_data, parent=None):
        super().__init__(parent)
        self.clip_data = clip_data
        self.pixels_per_sec = 10
        self._dragging = False
        self._resizing = None
        self._drag_start_x = 0
        self._orig_geometry = None
        self.is_selected = False

        w = max(60, int(
            (clip_data.get("trim_end", clip_data.get("duration", 1))
             - clip_data.get("trim_start", 0)) * self.pixels_per_sec
        ))
        self.setFixedSize(w, 60)
        self._apply_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)

        name = os.path.basename(clip_data.get("path", "clip"))
        if len(name) > 18:
            name = name[:15] + "..."
        self.title = QLabel(f"🎬 {name}")
        self.title.setStyleSheet(
            "color: white; font-weight: bold; font-size: 11px;"
        )
        layout.addWidget(self.title)

        self.info = QLabel(self._info_text())
        self.info.setStyleSheet("color: #eee; font-size: 10px;")
        layout.addWidget(self.info)

        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

    def _apply_style(self):
        if self.is_selected:
            self.setStyleSheet("""
                ClipWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffb84d, stop:1 #ff8c1a);
                    border-radius: 6px;
                    border: 3px solid #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                ClipWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #7c5cff, stop:1 #5a3fd6);
                    border-radius: 6px;
                    border: 2px solid #9b7cff;
                }
                ClipWidget:hover { border: 2px solid #ffffff; }
            """)

    def set_selected(self, val):
        self.is_selected = val
        self._apply_style()

    def _info_text(self):
        s = self.clip_data.get("trim_start", 0)
        e = self.clip_data.get("trim_end", self.clip_data.get("duration", 0))
        speed = self.clip_data.get("speed", 1.0)
        extra = f" | {speed}x" if speed != 1.0 else ""
        return f"⏱ {e - s:.1f}s{extra}"

    def update_ui(self):
        w = max(40, int(
            (self.clip_data.get("trim_end", 0)
             - self.clip_data.get("trim_start", 0)) * self.pixels_per_sec
        ))
        self.setFixedWidth(w)
        self.info.setText(self._info_text())

    def set_zoom(self, pps):
        self.pixels_per_sec = pps
        self.update_ui()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        self._drag_start_x = event.globalPosition().toPoint().x()
        self._orig_geometry = self.geometry()
        local_x = event.position().x()

        if local_x < self.HANDLE_WIDTH:
            self._resizing = "left"
            self.setCursor(Qt.SizeHorCursor)
        elif local_x > self.width() - self.HANDLE_WIDTH:
            self._resizing = "right"
            self.setCursor(Qt.SizeHorCursor)
        else:
            self._dragging = True
            self.setCursor(Qt.ClosedHandCursor)

        self.clicked.emit(self)
        event.accept()

    def mouseMoveEvent(self, event):
        local_x = event.position().x()
        if not self._dragging and not self._resizing:
            if (local_x < self.HANDLE_WIDTH
                    or local_x > self.width() - self.HANDLE_WIDTH):
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.OpenHandCursor)
            return

        dx = event.globalPosition().toPoint().x() - self._drag_start_x

        if self._dragging:
            new_x = self._orig_geometry.x() + dx
            self.move(max(0, new_x), self.y())

            parent = self.parent()
            while parent and not hasattr(parent, "snap_check"):
                parent = parent.parent()
            if parent and parent.snap_enabled:
                parent.snap_check(self)

        elif self._resizing == "left":
            new_w = max(40, self._orig_geometry.width() - dx)
            new_x = self._orig_geometry.x() + (
                self._orig_geometry.width() - new_w)
            self.setFixedWidth(new_w)
            self.move(max(0, new_x), self.y())
            delta_sec = dx / self.pixels_per_sec
            self.clip_data["trim_start"] = max(
                0, self.clip_data.get("trim_start", 0) + delta_sec
            )
            self.info.setText(self._info_text())

        elif self._resizing == "right":
            new_w = max(40, self._orig_geometry.width() + dx)
            self.setFixedWidth(new_w)
            delta_sec = dx / self.pixels_per_sec
            new_end = self.clip_data.get("trim_end", 0) + delta_sec
            new_end = min(new_end, self.clip_data.get("duration", new_end))
            self.clip_data["trim_end"] = new_end
            self.info.setText(self._info_text())

        event.accept()

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self.moved.emit(self, self.x())
        elif self._resizing:
            self.resized.emit(
                self,
                self.clip_data.get("trim_start", 0),
                self.clip_data.get("trim_end", 0)
            )
        self._dragging = False
        self._resizing = None
        self.setCursor(Qt.OpenHandCursor)
        event.accept()

    def show_menu(self, pos):
        menu = QMenu(self)

        split_action = menu.addAction("✂ Split at Playhead")
        duplicate_action = menu.addAction("📋 Duplicate (Ctrl+D)")
        copy_action = menu.addAction("📄 Copy (Ctrl+C)")

        menu.addSeparator()
        speed_menu = menu.addMenu("⚡ Speed")
        speed_actions = {
            speed_menu.addAction("0.25x"): 0.25,
            speed_menu.addAction("0.5x"): 0.5,
            speed_menu.addAction("1.0x (Normal)"): 1.0,
            speed_menu.addAction("1.5x"): 1.5,
            speed_menu.addAction("2.0x"): 2.0,
            speed_menu.addAction("4.0x"): 4.0,
        }

        menu.addSeparator()
        color_menu = menu.addMenu("🎨 Color تبدیل کریں")
        color_actions = {
            color_menu.addAction("🟣 جامنی"): "#7c5cff",
            color_menu.addAction("🟢 سبز"): "#4caf50",
            color_menu.addAction("🔵 نیلا"): "#2196f3",
            color_menu.addAction("🟡 پیلا"): "#ffb84d",
            color_menu.addAction("🔴 سرخ"): "#f44336",
            color_menu.addAction("🟠 نارنجی"): "#ff9800",
        }

        menu.addSeparator()
        delete_action = menu.addAction("🗑 ڈیلیٹ کریں")

        action = menu.exec_(self.mapToGlobal(pos))

        if action == split_action:
            parent = self.parent()
            while parent and not hasattr(parent, "playhead_time"):
                parent = parent.parent()
            if parent:
                self.split_requested.emit(self, parent.playhead_time)
        elif action == duplicate_action:
            self.duplicate_requested.emit(self)
        elif action == copy_action:
            self.copy_requested.emit(self)
        elif action in speed_actions:
            self.clip_data["speed"] = speed_actions[action]
            self.info.setText(self._info_text())
        elif action in color_actions:
            color = color_actions[action]
            self.setStyleSheet(f"""
                ClipWidget {{
                    background: {color};
                    border-radius: 6px;
                    border: 2px solid #fff;
                }}
            """)
            self.clip_data["color"] = color
        elif action == delete_action:
            self.deleted.emit(self)


# ==================== Track Widget ====================
class TrackWidget(QWidget):
    def __init__(self, name, color="#2a2a2a"):
        super().__init__()
        self.name = name
        self.clips = []
        self.setMinimumHeight(80)
        self.setStyleSheet(
            f"TrackWidget {{ background: {color}; "
            f"border-bottom: 1px solid #333; }}"
        )
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(4)
        self.layout.addStretch()

    def add_clip(self, clip_widget, index=None):
        self.clips.append(clip_widget)
        if index is not None:
            self.layout.insertWidget(index, clip_widget)
        else:
            self.layout.insertWidget(self.layout.count() - 1, clip_widget)
        clip_widget.deleted.connect(self.remove_clip)

    def remove_clip(self, clip_widget):
        if clip_widget in self.clips:
            self.clips.remove(clip_widget)
            clip_widget.setParent(None)
            clip_widget.deleteLater()

    def clear(self):
        for c in list(self.clips):
            c.setParent(None)
            c.deleteLater()
        self.clips.clear()


# ==================== Playhead ====================
class Playhead(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedWidth(2)
        self.setStyleSheet("background: #ff3b3b;")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()


# ==================== Timeline V2 ====================
class TimelineV2(QWidget):
    clip_selected = Signal(dict)
    time_changed = Signal(float)
    state_changed = Signal()

    def __init__(self):
        super().__init__()
        self.pixels_per_sec = 10
        self.playhead_time = 0.0
        self.project_mgr = ProjectManager()
        self.clipboard = None
        self.selected_clip = None
        self.snap_enabled = True
        self.markers = []
        self.marker_widgets = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ---------- Header ----------
        header = QHBoxLayout()
        header.addWidget(QLabel("🕒 Timeline"))

        self.info_label = QLabel("0 کلپس | 0.0s")
        self.info_label.setStyleSheet("color: #888;")
        header.addWidget(self.info_label)

        header.addStretch()

        # Snap toggle
        self.snap_cb = QCheckBox("🧲 Snap")
        self.snap_cb.setChecked(True)
        self.snap_cb.setStyleSheet("color: #ccc;")
        self.snap_cb.stateChanged.connect(self._toggle_snap)
        header.addWidget(self.snap_cb)

        # Marker بٹن
        marker_btn = QPushButton("🔴 Marker")
        marker_btn.setFixedWidth(90)
        marker_btn.clicked.connect(
            lambda: self.add_marker_at_playhead("Marker", "#ff3b3b"))
        header.addWidget(marker_btn)

        clear_marker_btn = QPushButton("✖ Markers")
        clear_marker_btn.setFixedWidth(90)
        clear_marker_btn.clicked.connect(self.clear_markers)
        header.addWidget(clear_marker_btn)

        # Undo / Redo
        self.undo_btn = QPushButton("↶")
        self.undo_btn.setFixedWidth(35)
        self.undo_btn.clicked.connect(self.undo)
        header.addWidget(self.undo_btn)

        self.redo_btn = QPushButton("↷")
        self.redo_btn.setFixedWidth(35)
        self.redo_btn.clicked.connect(self.redo)
        header.addWidget(self.redo_btn)

        # Zoom
        header.addWidget(QLabel("🔍"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(2, 100)
        self.zoom_slider.setValue(10)
        self.zoom_slider.setFixedWidth(120)
        self.zoom_slider.valueChanged.connect(self.on_zoom)
        header.addWidget(self.zoom_slider)

        main_layout.addLayout(header)

        # ---------- Ruler ----------
        self.ruler = QLabel(
            "0s    2s    4s    6s    8s   10s   12s   14s   16s   18s   20s"
        )
        self.ruler.setStyleSheet("""
            background: #202020; color: #666;
            padding: 4px 10px; font-family: monospace;
            border-top: 1px solid #333;
            border-bottom: 1px solid #333;
        """)
        self.ruler.setFixedHeight(24)
        main_layout.addWidget(self.ruler)

        # ---------- Scroll ----------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: 1px solid #333; border-radius: 6px;
                          background: #1a1a1a; }
        """)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        # 🔥 Multi Video Tracks + Audio Tracks
        self.video_track = TrackWidget("Video 1", "#252525")
        self.video_track_2 = TrackWidget("Video 2", "#2a2530")
        self.video_track_3 = TrackWidget("Video 3", "#252a30")
        self.audio_track = TrackWidget("Audio 1", "#1f1f1f")
        self.audio_track_2 = TrackWidget("Audio 2", "#1f2320")

        self.container_layout.addWidget(
            self._make_track_label("🎞 Video Track 1"))
        self.container_layout.addWidget(self.video_track)
        self.container_layout.addWidget(
            self._make_track_label("🎞 Video Track 2 (Overlay)"))
        self.container_layout.addWidget(self.video_track_2)
        self.container_layout.addWidget(
            self._make_track_label("🎞 Video Track 3 (Overlay)"))
        self.container_layout.addWidget(self.video_track_3)
        self.container_layout.addWidget(
            self._make_track_label("🔊 Audio Track 1"))
        self.container_layout.addWidget(self.audio_track)
        self.container_layout.addWidget(
            self._make_track_label("🔊 Audio Track 2"))
        self.container_layout.addWidget(self.audio_track_2)
        self.container_layout.addStretch()

        scroll.setWidget(self.container)
        main_layout.addWidget(scroll)

        self.playhead = Playhead(self.container)
        self.container.mousePressEvent = self._on_container_click

        self.project_mgr.save_state(self.get_state())

    def _make_track_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
            color: #aaa; padding: 4px 10px;
            background: #202020; font-weight: bold;
            border-top: 1px solid #333;
        """)
        label.setFixedHeight(24)
        return label

    def _toggle_snap(self, state):
        # Qt.Checked = 2 (PySide6)
        try:
            self.snap_enabled = (state == Qt.CheckState.Checked.value
                                 or state == 2)
        except Exception:
            self.snap_enabled = bool(state)

    def _on_container_click(self, event):
        if event.button() == Qt.LeftButton:
            x = event.position().x()
            self.set_playhead_from_x(x)
            if self.selected_clip:
                self.selected_clip.set_selected(False)
                self.selected_clip = None
        event.accept()

    def set_playhead_from_x(self, x):
        self.playhead_time = x / self.pixels_per_sec
        self.playhead.setGeometry(int(x), 0, 2, self.container.height())
        self.playhead.show()
        self.time_changed.emit(self.playhead_time)
        self._update_info()

    def set_playhead_time(self, sec):
        self.playhead_time = sec
        x = int(sec * self.pixels_per_sec)
        self.playhead.setGeometry(x, 0, 2, self.container.height())
        self.playhead.show()
        self._update_info()

    def _update_info(self):
        total = (len(self.video_track.clips) + len(self.video_track_2.clips)
                 + len(self.video_track_3.clips))
        self.info_label.setText(
            f"{total} کلپس | {self.playhead_time:.1f}s | "
            f"{len(self.markers)} 🔴"
        )

    def on_zoom(self, val):
        self.pixels_per_sec = val
        for track in [self.video_track, self.video_track_2,
                      self.video_track_3, self.audio_track, self.audio_track_2]:
            for clip in track.clips:
                clip.set_zoom(val)
        self._update_info()

    # ---------- Snap ----------
    def snap_check(self, clip):
        if not self.snap_enabled:
            return
        snap_dist = 10
        all_clips = []
        for track in [self.video_track, self.video_track_2, self.video_track_3]:
            all_clips.extend(track.clips)
        others = [c for c in all_clips if c is not clip]
        for other in others:
            if abs(clip.x() - (other.x() + other.width())) < snap_dist:
                clip.move(other.x() + other.width(), clip.y())
                return
            if abs(clip.x() + clip.width() - other.x()) < snap_dist:
                clip.move(other.x() - clip.width(), clip.y())
                return

    # ---------- Markers ----------
    def add_marker_at_playhead(self, label="Marker", color="#ff3b3b"):
        """موجودہ playhead پر مارکر لگائیں"""
        from PySide6.QtWidgets import QLabel
        self.markers.append({
            "time": self.playhead_time, "label": label, "color": color
        })

        marker = QLabel(self.container)
        marker.setStyleSheet(f"background: {color}; border-radius: 2px;")
        marker.setFixedSize(3, self.container.height())
        marker.move(int(self.playhead_time * self.pixels_per_sec), 0)
        marker.show()
        marker.setToolTip(f"{label} @ {self.playhead_time:.2f}s")
        self.marker_widgets.append(marker)
        self._update_info()
        print(f"🔴 Marker @ {self.playhead_time:.2f}s")

    def clear_markers(self):
        for m in self.marker_widgets:
            m.setParent(None)
            m.deleteLater()
        self.marker_widgets.clear()
        self.markers.clear()
        self._update_info()

    # ---------- State ----------
    def get_state(self):
        return {
            "video_track": [dict(c.clip_data) for c in self.video_track.clips],
            "video_track_2": [dict(c.clip_data) for c in self.video_track_2.clips],
            "video_track_3": [dict(c.clip_data) for c in self.video_track_3.clips],
            "markers": list(self.markers),
        }

    def restore_state(self, state):
        if isinstance(state, list):
            state = {"video_track": state, "video_track_2": [],
                     "video_track_3": [], "markers": []}

        for track, key in [
            (self.video_track, "video_track"),
            (self.video_track_2, "video_track_2"),
            (self.video_track_3, "video_track_3"),
        ]:
            track.clear()
            for data in state.get(key, []):
                clip = ClipWidget(data)
                clip.set_zoom(self.pixels_per_sec)
                clip.clicked.connect(self.on_clip_clicked)
                clip.split_requested.connect(self.on_split)
                clip.duplicate_requested.connect(self.duplicate_clip)
                clip.copy_requested.connect(self.copy_clip)
                if "color" in data:
                    clip.setStyleSheet(f"""
                        ClipWidget {{
                            background: {data['color']};
                            border-radius: 6px;
                            border: 2px solid #fff;
                        }}
                    """)
                track.add_clip(clip)

        # مارکر بحال کریں
        self.clear_markers()
        for m in state.get("markers", []):
            self.markers.append(m)
            from PySide6.QtWidgets import QLabel
            marker = QLabel(self.container)
            marker.setStyleSheet(
                f"background: {m['color']}; border-radius: 2px;")
            marker.setFixedSize(3, self.container.height())
            marker.move(int(m["time"] * self.pixels_per_sec), 0)
            marker.show()
            self.marker_widgets.append(marker)

        self._update_info()

    def undo(self):
        if not self.project_mgr.can_undo():
            return
        state = self.project_mgr.undo(self.get_state())
        if state is not None:
            self.restore_state(state)

    def redo(self):
        state = self.project_mgr.redo(self.get_state())
        if state is not None:
            self.restore_state(state)

    # ---------- Add Clip ----------
    def _probe_duration(self, path):
        try:
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", path
            ], capture_output=True, text=True)
            data = json.loads(result.stdout)
            return float(data["format"]["duration"])
        except Exception:
            return 5.0

    def add_clip(self, path):
        duration = self._probe_duration(path)
        clip_data = {
            "path": path,
            "duration": duration,
            "trim_start": 0,
            "trim_end": duration,
            "speed": 1.0,
        }
        clip = ClipWidget(clip_data)
        clip.set_zoom(self.pixels_per_sec)
        clip.clicked.connect(self.on_clip_clicked)
        clip.split_requested.connect(self.on_split)
        clip.duplicate_requested.connect(self.duplicate_clip)
        clip.copy_requested.connect(self.copy_clip)

        self.video_track.add_clip(clip)
        self.project_mgr.save_state(self.get_state())
        self._update_info()

    def add_clip_to_track(self, path, track_index=1):
        tracks = {1: self.video_track, 2: self.video_track_2,
                  3: self.video_track_3}
        track = tracks.get(track_index, self.video_track)

        duration = self._probe_duration(path)
        clip_data = {
            "path": path,
            "duration": duration,
            "trim_start": 0,
            "trim_end": duration,
            "speed": 1.0,
        }
        clip = ClipWidget(clip_data)
        clip.set_zoom(self.pixels_per_sec)
        clip.clicked.connect(self.on_clip_clicked)
        clip.split_requested.connect(self.on_split)
        clip.duplicate_requested.connect(self.duplicate_clip)
        clip.copy_requested.connect(self.copy_clip)

        track.add_clip(clip)
        self.project_mgr.save_state(self.get_state())
        self._update_info()

    def on_clip_clicked(self, clip_widget):
        if self.selected_clip and self.selected_clip is not clip_widget:
            self.selected_clip.set_selected(False)
        clip_widget.set_selected(True)
        self.selected_clip = clip_widget
        self.clip_selected.emit(clip_widget.clip_data)

    # ---------- Split ----------
    def on_split(self, clip_widget, at_time):
        result = ClipOperations.split_clip(clip_widget.clip_data, at_time)
        if not result:
            return
        left, right = result
        # speed محفوظ
        left["speed"] = clip_widget.clip_data.get("speed", 1.0)
        right["speed"] = clip_widget.clip_data.get("speed", 1.0)

        for track in [self.video_track, self.video_track_2, self.video_track_3]:
            if clip_widget in track.clips:
                idx = track.clips.index(clip_widget)
                track.remove_clip(clip_widget)

                for i, data in enumerate([left, right]):
                    c = ClipWidget(data)
                    c.set_zoom(self.pixels_per_sec)
                    c.clicked.connect(self.on_clip_clicked)
                    c.split_requested.connect(self.on_split)
                    c.duplicate_requested.connect(self.duplicate_clip)
                    c.copy_requested.connect(self.copy_clip)
                    track.add_clip(c, index=idx + i)
                break

        self.project_mgr.save_state(self.get_state())
        self._update_info()

    # ---------- Copy / Paste / Duplicate ----------
    def copy_clip(self, clip_widget):
        self.clipboard = copy.deepcopy(clip_widget.clip_data)
        print("📄 کاپی ہو گیا")

    def copy_selected(self):
        if self.selected_clip is None:
            return False
        self.clipboard = copy.deepcopy(self.selected_clip.clip_data)
        return True

    def paste_clip(self):
        if self.clipboard is None:
            return False
        data = copy.deepcopy(self.clipboard)
        clip = ClipWidget(data)
        clip.set_zoom(self.pixels_per_sec)
        clip.clicked.connect(self.on_clip_clicked)
        clip.split_requested.connect(self.on_split)
        clip.duplicate_requested.connect(self.duplicate_clip)
        clip.copy_requested.connect(self.copy_clip)
        self.video_track.add_clip(clip)
        self.project_mgr.save_state(self.get_state())
        self._update_info()
        return True

    def duplicate_clip(self, clip_widget):
        data = copy.deepcopy(clip_widget.clip_data)
        clip = ClipWidget(data)
        clip.set_zoom(self.pixels_per_sec)
        clip.clicked.connect(self.on_clip_clicked)
        clip.split_requested.connect(self.on_split)
        clip.duplicate_requested.connect(self.duplicate_clip)
        clip.copy_requested.connect(self.copy_clip)

        for track in [self.video_track, self.video_track_2, self.video_track_3]:
            if clip_widget in track.clips:
                track.add_clip(clip)
                break

        self.project_mgr.save_state(self.get_state())
        self._update_info()

    def delete_selected(self):
        if self.selected_clip is None:
            return
        for track in [self.video_track, self.video_track_2, self.video_track_3]:
            if self.selected_clip in track.clips:
                track.remove_clip(self.selected_clip)
                break
        self.selected_clip = None
        self.project_mgr.save_state(self.get_state())
        self._update_info()