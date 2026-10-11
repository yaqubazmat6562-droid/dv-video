import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QMessageBox, QComboBox, QProgressBar
)
from PySide6.QtCore import QThread, Signal
from ai.captions import CaptionGenerator


class CaptionWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, video_path, model_size):
        super().__init__()
        self.video_path = video_path
        self.model_size = model_size

    def run(self):
        try:
            gen = CaptionGenerator(model_size=self.model_size)
            result = gen.transcribe(self.video_path)
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("Transcription failed")
        except Exception as e:
            self.error.emit(str(e))


class AIPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_video = None
        self.srt_path = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🤖 AI Features"))

        layout.addWidget(QLabel("Whisper Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium"])
        self.model_combo.setCurrentText("base")
        layout.addWidget(self.model_combo)

        self.caption_btn = QPushButton("🎙 Auto Captions بنائیں")
        self.caption_btn.clicked.connect(self.generate_captions)
        layout.addWidget(self.caption_btn)

        self.burn_btn = QPushButton("🔥 Subtitles ویڈیو پر لگائیں")
        self.burn_btn.clicked.connect(self.burn_subtitles)
        self.burn_btn.setEnabled(False)
        layout.addWidget(self.burn_btn)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        layout.addStretch()

    def set_video(self, path):
        self.current_video = path
        self.srt_path = None
        self.burn_btn.setEnabled(False)
        self.status.setText(f"📹 {os.path.basename(path)}")

    def generate_captions(self):
        if not self.current_video:
            QMessageBox.warning(self, "Error", "پہلے ویڈیو منتخب کریں")
            return

        self.progress.setVisible(True)
        self.caption_btn.setEnabled(False)
        self.status.setText("⏳ Whisper چل رہا ہے... پہلی بار 2-5 منٹ لگ سکتے ہیں")

        model_size = self.model_combo.currentText()
        self.worker = CaptionWorker(self.current_video, model_size)
        self.worker.finished.connect(self.on_captions_done)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_captions_done(self, result):
        self.progress.setVisible(False)
        self.caption_btn.setEnabled(True)

        segments = result.get("segments", [])
        if not segments:
            self.status.setText("❌ کوئی آواز نہیں ملی")
            return

        gen = CaptionGenerator()
        srt_path = os.path.splitext(self.current_video)[0] + ".srt"
        gen.save_srt(segments, srt_path)
        self.srt_path = srt_path

        self.status.setText(f"✅ {len(segments)} سب ٹائٹلز بن گئے")
        self.burn_btn.setEnabled(True)
        QMessageBox.information(self, "کامیاب",
                                f"{len(segments)} سب ٹائٹلز بن گئے!")

    def on_error(self, msg):
        self.progress.setVisible(False)
        self.caption_btn.setEnabled(True)
        self.status.setText(f"❌ {msg}")
        QMessageBox.critical(self, "Error", msg)

    def burn_subtitles(self):
        if not self.srt_path or not os.path.exists(self.srt_path):
            QMessageBox.warning(self, "Error", "پہلے سب ٹائٹلز بنائیں")
            return

        output = os.path.splitext(self.current_video)[0] + "_subtitled.mp4"
        self.status.setText("⏳ Subtitles لگ رہے ہیں...")
        self.progress.setVisible(True)

        gen = CaptionGenerator()
        ok, msg = gen.burn_subtitles(self.current_video, self.srt_path, output)

        self.progress.setVisible(False)

        if ok:
            self.status.setText(f"✅ محفوظ: {output}")
            QMessageBox.information(self, "کامیاب", f"ویڈیو محفوظ:\n{output}")
        else:
            self.status.setText(f"❌ {msg}")
            QMessageBox.critical(self, "Error", msg)