import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
from core.filters import VideoFilters, Transitions, ZoomPan


class FiltersPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_video = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🎨 Filters & Effects"))

        # ---------- Presets ----------
        box1 = QGroupBox("Color Preset")
        box1.setStyleSheet("QGroupBox { color:#aaa; }")
        v1 = QVBoxLayout(box1)

        self.preset = QComboBox()
        self.preset.addItems(list(VideoFilters.PRESETS.keys()))
        v1.addWidget(self.preset)
        layout.addWidget(box1)

        # ---------- Manual Adjustments ----------
        box2 = QGroupBox("Manual Adjustments")
        box2.setStyleSheet("QGroupBox { color:#aaa; }")
        v2 = QVBoxLayout(box2)

        v2.addWidget(QLabel("Brightness"))
        self.brightness = QSlider(Qt.Horizontal)
        self.brightness.setRange(-100, 100)
        self.brightness.setValue(0)
        v2.addWidget(self.brightness)

        v2.addWidget(QLabel("Contrast"))
        self.contrast = QSlider(Qt.Horizontal)
        self.contrast.setRange(50, 200)
        self.contrast.setValue(100)
        v2.addWidget(self.contrast)

        v2.addWidget(QLabel("Saturation"))
        self.saturation = QSlider(Qt.Horizontal)
        self.saturation.setRange(0, 200)
        self.saturation.setValue(100)
        v2.addWidget(self.saturation)

        layout.addWidget(box2)

        # ---------- Apply ----------
        apply_btn = QPushButton("✅ Filter لگائیں")
        apply_btn.clicked.connect(self.apply_filter)
        layout.addWidget(apply_btn)

        # ---------- Fade In/Out ----------
        box3 = QGroupBox("Fade In / Out")
        box3.setStyleSheet("QGroupBox { color:#aaa; }")
        v3 = QVBoxLayout(box3)

        v3.addWidget(QLabel("Fade In (sec)"))
        self.fade_in = QSlider(Qt.Horizontal)
        self.fade_in.setRange(0, 5)
        self.fade_in.setValue(1)
        v3.addWidget(self.fade_in)

        v3.addWidget(QLabel("Fade Out (sec)"))
        self.fade_out = QSlider(Qt.Horizontal)
        self.fade_out.setRange(0, 5)
        self.fade_out.setValue(1)
        v3.addWidget(self.fade_out)

        fade_btn = QPushButton("🎬 Fade لگائیں")
        fade_btn.clicked.connect(self.apply_fade)
        v3.addWidget(fade_btn)

        layout.addWidget(box3)

        # ---------- Zoom Pan ----------
        box4 = QGroupBox("Zoom (Ken Burns)")
        box4.setStyleSheet("QGroupBox { color:#aaa; }")
        v4 = QVBoxLayout(box4)

        v4.addWidget(QLabel("Zoom Start"))
        self.zoom_start = QSlider(Qt.Horizontal)
        self.zoom_start.setRange(100, 300)
        self.zoom_start.setValue(100)
        v4.addWidget(self.zoom_start)

        v4.addWidget(QLabel("Zoom End"))
        self.zoom_end = QSlider(Qt.Horizontal)
        self.zoom_end.setRange(100, 300)
        self.zoom_end.setValue(150)
        v4.addWidget(self.zoom_end)

        zoom_btn = QPushButton("🔍 Zoom لگائیں")
        zoom_btn.clicked.connect(self.apply_zoom)
        v4.addWidget(zoom_btn)

        layout.addWidget(box4)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch()

    def set_video(self, path):
        self.current_video = path
        self.status.setText(f"📹 {os.path.basename(path)}")

    def _check(self):
        if not self.current_video:
            QMessageBox.warning(self, "Error", "پہلے ویڈیو منتخب کریں")
            return False
        return True

    def apply_filter(self):
        if not self._check():
            return
        output = os.path.splitext(self.current_video)[0] + "_filtered.mp4"

        ok, msg = VideoFilters.apply_filter(
            self.current_video, output,
            preset=self.preset.currentText(),
            brightness=self.brightness.value() / 100.0,
            contrast=self.contrast.value() / 100.0,
            saturation=self.saturation.value() / 100.0,
        )
        self._show_result(ok, msg, output)

    def apply_fade(self):
        if not self._check():
            return
        output = os.path.splitext(self.current_video)[0] + "_fade.mp4"
        ok, msg = Transitions.fade_in_out(
            self.current_video, output,
            fade_in=self.fade_in.value(),
            fade_out=self.fade_out.value(),
        )
        self._show_result(ok, msg, output)

    def apply_zoom(self):
        if not self._check():
            return
        output = os.path.splitext(self.current_video)[0] + "_zoom.mp4"
        ok, msg = ZoomPan.apply_zoom(
            self.current_video, output,
            zoom_start=self.zoom_start.value() / 100.0,
            zoom_end=self.zoom_end.value() / 100.0,
        )
        self._show_result(ok, msg, output)

    def _show_result(self, ok, msg, output):
        if ok:
            self.status.setText(f"✅ محفوظ: {output}")
            QMessageBox.information(self, "کامیاب", f"فائل بن گئی:\n{output}")
        else:
            self.status.setText(f"❌ {msg}")
            QMessageBox.critical(self, "Error", msg)