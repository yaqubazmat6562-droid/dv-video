import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QMessageBox, QGroupBox,
    QHBoxLayout, QFileDialog, QSpinBox
)
from PySide6.QtCore import Qt
from core.effects import Effects, ImageOverlay, AudioMixer


class EffectsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_video = None
        self.image_path = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("✨ Effects & Overlays"))

        # ---------- Effects ----------
        box1 = QGroupBox("Video Effects")
        v1 = QVBoxLayout(box1)

        self.effect_combo = QComboBox()
        self.effect_combo.addItems(list(Effects.EFFECTS.keys()))
        v1.addWidget(self.effect_combo)

        apply_effect = QPushButton("✅ Effect لگائیں")
        apply_effect.clicked.connect(self.apply_effect)
        v1.addWidget(apply_effect)

        layout.addWidget(box1)

        # ---------- Stickers ----------
        box2 = QGroupBox("Sticker / Image Overlay")
        v2 = QVBoxLayout(box2)

        pick_btn = QPushButton("🖼 تصویر منتخب کریں")
        pick_btn.clicked.connect(self.pick_image)
        v2.addWidget(pick_btn)

        self.image_label = QLabel("کوئی تصویر نہیں")
        self.image_label.setStyleSheet("color: #888; font-size: 10px;")
        v2.addWidget(self.image_label)

        v2.addWidget(QLabel("Position:"))
        self.overlay_pos = QComboBox()
        self.overlay_pos.addItems(list(ImageOverlay.POSITIONS.keys()))
        self.overlay_pos.setCurrentText("نیچے دائیں")
        v2.addWidget(self.overlay_pos)

        v2.addWidget(QLabel("Scale:"))
        self.overlay_scale = QSlider(Qt.Horizontal)
        self.overlay_scale.setRange(5, 200)
        self.overlay_scale.setValue(30)
        v2.addWidget(self.overlay_scale)

        v2.addWidget(QLabel("Opacity:"))
        self.overlay_opacity = QSlider(Qt.Horizontal)
        self.overlay_opacity.setRange(10, 100)
        self.overlay_opacity.setValue(100)
        v2.addWidget(self.overlay_opacity)

        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("Start:"))
        self.ov_start = QSpinBox()
        self.ov_start.setRange(0, 9999)
        time_row.addWidget(self.ov_start)
        time_row.addWidget(QLabel("End:"))
        self.ov_end = QSpinBox()
        self.ov_end.setRange(0, 9999)
        time_row.addWidget(self.ov_end)
        v2.addLayout(time_row)

        apply_overlay = QPushButton("🖼 Sticker لگائیں")
        apply_overlay.clicked.connect(self.apply_overlay)
        v2.addWidget(apply_overlay)

        layout.addWidget(box2)

        # ---------- Audio ----------
        box3 = QGroupBox("Audio")
        v3 = QVBoxLayout(box3)

        v3.addWidget(QLabel("Volume:"))
        self.audio_volume = QSlider(Qt.Horizontal)
        self.audio_volume.setRange(0, 200)
        self.audio_volume.setValue(100)
        v3.addWidget(self.audio_volume)

        vol_btn = QPushButton("🔊 Volume لگائیں")
        vol_btn.clicked.connect(self.apply_volume)
        v3.addWidget(vol_btn)

        mute_btn = QPushButton("🔇 آواز بند کریں")
        mute_btn.clicked.connect(self.mute_audio)
        v3.addWidget(mute_btn)

        extract_btn = QPushButton("🎵 آواز نکالیں (MP3)")
        extract_btn.clicked.connect(self.extract_audio)
        v3.addWidget(extract_btn)

        layout.addWidget(box3)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch()

    def set_video(self, path):
        self.current_video = path
        self.status.setText(f"📹 {os.path.basename(path)}")

    def pick_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self.image_path = path
            self.image_label.setText(os.path.basename(path))

    def _check(self):
        if not self.current_video:
            QMessageBox.warning(self, "Error", "پہلے ویڈیو منتخب کریں")
            return False
        return True

    def apply_effect(self):
        if not self._check():
            return
        output = os.path.splitext(self.current_video)[0] + "_effect.mp4"
        ok, msg = Effects.apply(
            self.current_video, output,
            effect=self.effect_combo.currentText()
        )
        self._show(ok, msg, output)

    def apply_overlay(self):
        if not self._check():
            return
        if not self.image_path:
            QMessageBox.warning(self, "Error", "پہلے تصویر منتخب کریں")
            return

        output = os.path.splitext(self.current_video)[0] + "_sticker.mp4"
        end = self.ov_end.value() if self.ov_end.value() > 0 else None

        ok, msg = ImageOverlay.overlay(
            self.current_video, self.image_path, output,
            position=self.overlay_pos.currentText(),
            scale=self.overlay_scale.value() / 100.0,
            start=self.ov_start.value(),
            end=end,
            opacity=self.overlay_opacity.value() / 100.0,
        )
        self._show(ok, msg, output)

    def apply_volume(self):
        if not self._check():
            return
        output = os.path.splitext(self.current_video)[0] + "_vol.mp4"
        ok, msg = AudioMixer.set_volume(
            self.current_video, output,
            volume=self.audio_volume.value() / 100.0
        )
        self._show(ok, msg, output)

    def mute_audio(self):
        if not self._check():
            return
        output = os.path.splitext(self.current_video)[0] + "_mute.mp4"
        ok, msg = AudioMixer.mute(self.current_video, output)
        self._show(ok, msg, output)

    def extract_audio(self):
        if not self._check():
            return
        output = os.path.splitext(self.current_video)[0] + "_audio.mp3"
        ok, msg = AudioMixer.extract_audio(self.current_video, output)
        self._show(ok, msg, output)

    def _show(self, ok, msg, output):
        if ok:
            self.status.setText(f"✅ محفوظ: {output}")
            QMessageBox.information(self, "کامیاب", f"فائل بنی:\n{output}")
        else:
            self.status.setText(f"❌ {msg}")
            QMessageBox.critical(self, "Error", msg)