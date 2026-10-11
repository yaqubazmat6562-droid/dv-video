import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox, QFileDialog, QGroupBox,
    QSlider, QSpinBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from core.audio_ducking import AudioDucking
from core.ai_style import AIStyle
from core.multi_export import MultiExport, ProxyGenerator
from core.motion_tracker import MotionTracker


class ProMaxPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_video = None
        self.music_path = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("⚡ Pro Max Features"))

        # ---------- AI Style ----------
        box1 = QGroupBox("🎨 AI Style Transfer")
        v1 = QVBoxLayout(box1)

        self.style_combo = QComboBox()
        self.style_combo.addItems(list(AIStyle.STYLES.keys()))
        v1.addWidget(self.style_combo)

        style_btn = QPushButton("✨ Style لگائیں")
        style_btn.clicked.connect(self.apply_style)
        v1.addWidget(style_btn)

        layout.addWidget(box1)

        # ---------- Audio Ducking ----------
        box2 = QGroupBox("🎵 Audio Ducking")
        v2 = QVBoxLayout(box2)

        music_btn = QPushButton("🎵 میوزک منتخب کریں")
        music_btn.clicked.connect(self.pick_music)
        v2.addWidget(music_btn)

        self.music_label = QLabel("کوئی میوزک نہیں")
        self.music_label.setStyleSheet("color: #888; font-size: 10px;")
        v2.addWidget(self.music_label)

        v2.addWidget(QLabel("Music Volume:"))
        self.music_vol = QSlider(Qt.Horizontal)
        self.music_vol.setRange(0, 100)
        self.music_vol.setValue(30)
        v2.addWidget(self.music_vol)

        duck_btn = QPushButton("🎵 Ducking لگائیں")
        duck_btn.clicked.connect(self.apply_ducking)
        v2.addWidget(duck_btn)

        sidechain_btn = QPushButton("🎵 Sidechain Ducking (Pro)")
        sidechain_btn.clicked.connect(self.apply_sidechain)
        v2.addWidget(sidechain_btn)

        layout.addWidget(box2)

        # ---------- Video Stabilization ----------
        box3 = QGroupBox("🌐 Stabilization")
        v3 = QVBoxLayout(box3)

        stab_btn = QPushButton("🌐 Video Stabilize کریں")
        stab_btn.clicked.connect(self.apply_stabilization)
        v3.addWidget(stab_btn)

        layout.addWidget(box3)

        # ---------- Multi Export ----------
        box4 = QGroupBox("📤 Multi Export")
        v4 = QVBoxLayout(box4)

        export_btn = QPushButton("📤 720p + 1080p ایک ساتھ")
        export_btn.clicked.connect(self.multi_export)
        v4.addWidget(export_btn)

        proxy_btn = QPushButton("🎞 Proxy بنائیں (1/2)")
        proxy_btn.clicked.connect(self.make_proxy)
        v4.addWidget(proxy_btn)

        layout.addWidget(box4)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch()

    def set_video(self, path):
        self.current_video = path
        self.status.setText(f"📹 {os.path.basename(path)}")

    def pick_music(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Music منتخب کریں", "",
            "Audio (*.mp3 *.wav *.m4a *.aac)"
        )
        if path:
            self.music_path = path
            self.music_label.setText(os.path.basename(path))

    def _check(self):
        if not self.current_video:
            QMessageBox.warning(self, "Error", "پہلے ویڈیو منتخب کریں")
            return False
        return True

    def apply_style(self):
        if not self._check():
            return
        output = os.path.splitext(self.current_video)[0] + "_style.mp4"
        QMessageBox.information(self, "انتظار", "AI Style لگ رہا ہے...")
        ok, msg = AIStyle.apply_style(
            self.current_video, output,
            style=self.style_combo.currentText()
        )
        self._show(ok, msg, output)

    def apply_ducking(self):
        if not self._check() or not self.music_path:
            QMessageBox.warning(self, "Error", "ویڈیو اور میوزک دونوں چاہیے")
            return
        output = os.path.splitext(self.current_video)[0] + "_ducked.mp4"
        ok, msg = AudioDucking.duck(
            self.current_video, self.music_path, output,
            music_volume=self.music_vol.value() / 100.0
        )
        self._show(ok, msg, output)

    def apply_sidechain(self):
        if not self._check() or not self.music_path:
            QMessageBox.warning(self, "Error", "ویڈیو اور میوزک دونوں چاہیے")
            return
        output = os.path.splitext(self.current_video)[0] + "_sidechain.mp4"
        QMessageBox.information(self, "انتظار", "Sidechain Ducking...")
        ok, msg = AudioDucking.sidechain_duck(
            self.current_video, self.music_path, output
        )
        self._show(ok, msg, output)

    def apply_stabilization(self):
        if not self._check():
            return
        output = os.path.splitext(self.current_video)[0] + "_stable.mp4"
        QMessageBox.information(self, "انتظار", "Stabilization (2 pass)...")
        ok, msg = MotionTracker.apply_stabilization(
            self.current_video, output
        )
        self._show(ok, msg, output)

    def multi_export(self):
        if not self._check():
            return
        out_dir = QFileDialog.getExistingDirectory(
            self, "Output Folder منتخب کریں"
        )
        if not out_dir:
            return
        base = os.path.splitext(os.path.basename(self.current_video))[0]
        QMessageBox.information(self, "انتظار", "Multi-export ہو رہا ہے...")
        results = MultiExport.export_versions(
            self.current_video, out_dir, base
        )
        success = sum(1 for _, ok, _ in results if ok)
        QMessageBox.information(
            self, "کامیاب", f"{success}/{len(results)} ورژن بن گئے"
        )

    def make_proxy(self):
        if not self._check():
            return
        output = os.path.splitext(self.current_video)[0] + "_proxy.mp4"
        ok, msg = ProxyGenerator.generate(self.current_video, output, 0.5)
        self._show(ok, msg, output)

    def _show(self, ok, msg, output):
        if ok:
            self.status.setText(f"✅ محفوظ: {output}")
            QMessageBox.information(self, "کامیاب", f"محفوظ:\n{output}")
        else:
            self.status.setText(f"❌ {msg}")
            QMessageBox.critical(self, "Error", msg)