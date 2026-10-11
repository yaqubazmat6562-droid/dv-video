import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QComboBox, QStackedLayout, QFrame
)
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtGui import QPainter, QColor, QPixmap


class PreviewWindow(QWidget):
    time_updated = Signal(float)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # ---------- Compositing Container ----------
        self.compositor = QFrame()
        self.compositor.setStyleSheet("background:#000; border-radius:8px;")
        self.compositor.setMinimumHeight(400)

        # 3 players (tracks)
        comp_layout = QStackedLayout(self.compositor)
        comp_layout.setStackingMode(QStackedLayout.StackAll)

        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background: transparent;")
        self.video_widget.setAttribute(Qt.WA_TranslucentBackground)

        self.video_widget_2 = QVideoWidget()
        self.video_widget_2.setStyleSheet("background: transparent;")
        self.video_widget_2.setAttribute(Qt.WA_TranslucentBackground)

        self.video_widget_3 = QVideoWidget()
        self.video_widget_3.setStyleSheet("background: transparent;")
        self.video_widget_3.setAttribute(Qt.WA_TranslucentBackground)

        comp_layout.addWidget(self.video_widget)
        comp_layout.addWidget(self.video_widget_2)
        comp_layout.addWidget(self.video_widget_3)

        layout.addWidget(self.compositor, stretch=1)

        # ---------- Players ----------
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        self.player_2 = QMediaPlayer()
        self.audio_output_2 = QAudioOutput()
        self.audio_output_2.setVolume(0.0)  # صرف ویڈیو
        self.player_2.setAudioOutput(self.audio_output_2)
        self.player_2.setVideoOutput(self.video_widget_2)

        self.player_3 = QMediaPlayer()
        self.audio_output_3 = QAudioOutput()
        self.audio_output_3.setVolume(0.0)
        self.player_3.setAudioOutput(self.audio_output_3)
        self.player_3.setVideoOutput(self.video_widget_3)

        # ---------- Position Slider ----------
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.position_slider)

        # ---------- Controls ----------
        controls = QHBoxLayout()

        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.toggle_play)
        controls.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop)
        controls.addWidget(self.stop_btn)

        self.time_label = QLabel("00:00 / 00:00")
        controls.addWidget(self.time_label)

        controls.addStretch()

        # Preview Quality
        controls.addWidget(QLabel("Quality:"))
        self.quality = QComboBox()
        self.quality.addItems(["Full", "Half", "Quarter"])
        self.quality.setCurrentText("Full")
        controls.addWidget(self.quality)

        layout.addLayout(controls)

        # Signals
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.playbackStateChanged.connect(self.on_state_changed)

        self.is_playing = False

    # ---------- Load ----------
    def load_video(self, path):
        if not os.path.exists(path):
            return
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()
        self.is_playing = True
        self.play_btn.setText("⏸ Pause")

    def load_track(self, path, track=1):
        """کسی مخصوص ٹریک پر لوڈ کریں"""
        if not os.path.exists(path):
            return
        if track == 1:
            self.player.setSource(QUrl.fromLocalFile(path))
            self.player.play()
        elif track == 2:
            self.player_2.setSource(QUrl.fromLocalFile(path))
            self.player_2.play()
        elif track == 3:
            self.player_3.setSource(QUrl.fromLocalFile(path))
            self.player_3.play()

    # ---------- Playback ----------
    def toggle_play(self):
        if self.is_playing:
            self.player.pause()
            self.player_2.pause()
            self.player_3.pause()
            self.play_btn.setText("▶ Play")
        else:
            self.player.play()
            self.player_2.play()
            self.player_3.play()
            self.play_btn.setText("⏸ Pause")
        self.is_playing = not self.is_playing

    def stop(self):
        self.player.stop()
        self.player_2.stop()
        self.player_3.stop()
        self.is_playing = False
        self.play_btn.setText("▶ Play")

    def set_position(self, position):
        self.player.setPosition(position)
        self.player_2.setPosition(position)
        self.player_3.setPosition(position)

    def update_position(self, position):
        self.position_slider.setValue(position)
        self.update_time_label(position, self.player.duration())
        self.time_updated.emit(position / 1000.0)

    def update_duration(self, duration):
        self.position_slider.setRange(0, duration)
        self.update_time_label(self.player.position(), duration)

    def update_time_label(self, pos, dur):
        def fmt(ms):
            s = ms // 1000
            return f"{s//60:02d}:{s%60:02d}"
        self.time_label.setText(f"{fmt(pos)} / {fmt(dur)}")

    def on_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText("⏸ Pause")
            self.is_playing = True
        else:
            self.play_btn.setText("▶ Play")
            self.is_playing = False