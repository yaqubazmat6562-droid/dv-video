import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSlider,
    QHBoxLayout, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt


class MixerChannel(QWidget):
    """ایک چینل کا volume + mute"""
    def __init__(self, name, color="#4caf50"):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        label = QLabel(name)
        label.setStyleSheet(f"color: {color}; font-weight: bold;")
        layout.addWidget(label)

        self.volume = QSlider(Qt.Vertical)
        self.volume.setRange(0, 200)
        self.volume.setValue(100)
        self.volume.setMinimumHeight(100)
        layout.addWidget(self.volume)

        self.vol_label = QLabel("100%")
        self.vol_label.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(self.vol_label)
        self.volume.valueChanged.connect(
            lambda v: self.vol_label.setText(f"{v}%")
        )

        self.mute = QCheckBox("Mute")
        self.mute.setStyleSheet("color: #ccc;")
        layout.addWidget(self.mute)


class MixerPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🎛 Audio Mixer"))

        row = QHBoxLayout()
        self.video1 = MixerChannel("Video 1", "#7c5cff")
        self.video2 = MixerChannel("Video 2", "#7c5cff")
        self.audio1 = MixerChannel("Audio 1", "#4caf50")
        self.audio2 = MixerChannel("Audio 2", "#4caf50")
        self.master = MixerChannel("Master", "#ff9800")

        for ch in [self.video1, self.video2, self.audio1,
                   self.audio2, self.master]:
            row.addWidget(ch)

        layout.addLayout(row)

        reset_btn = QPushButton("↺ Reset All")
        reset_btn.clicked.connect(self.reset_all)
        layout.addWidget(reset_btn)

        layout.addStretch()

    def reset_all(self):
        for ch in [self.video1, self.video2, self.audio1,
                   self.audio2, self.master]:
            ch.volume.setValue(100)
            ch.mute.setChecked(False)