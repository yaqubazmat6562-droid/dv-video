import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSlider, QFormLayout,
    QPushButton, QSpinBox, QComboBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from core.video_engine import VideoEngine


class PropertiesPanel(QWidget):
    # سگنل: جب ویڈیو تبدیل ہو
    video_processed = Signal(str)

    def __init__(self):
        super().__init__()
        self.current_video = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("⚙️ Properties"))

        form = QFormLayout()

        # Speed
        self.speed = QSlider(Qt.Horizontal)
        self.speed.setRange(25, 400)
        self.speed.setValue(100)
        self.speed_label = QLabel("1.00x")
        self.speed.valueChanged.connect(
            lambda v: self.speed_label.setText(f"{v/100:.2f}x")
        )
        form.addRow("Speed", self.speed)
        form.addRow("", self.speed_label)

        # Volume
        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(100)
        form.addRow("Volume", self.volume)

        # Trim Start
        self.trim_start = QSpinBox()
        self.trim_start.setRange(0, 99999)
        self.trim_start.setSuffix(" sec")
        form.addRow("Trim Start", self.trim_start)

        # Trim End
        self.trim_end = QSpinBox()
        self.trim_end.setRange(0, 99999)
        self.trim_end.setSuffix(" sec")
        form.addRow("Trim End", self.trim_end)

        layout.addLayout(form)
        layout.addSpacing(10)

        # Apply بٹن
        apply_btn = QPushButton("✅ Apply Changes")
        apply_btn.clicked.connect(self.apply_changes)
        layout.addWidget(apply_btn)

        # Export Section
        layout.addSpacing(20)
        layout.addWidget(QLabel("📤 Export"))

        export_form = QFormLayout()

        self.resolution = QComboBox()
        self.resolution.addItems(["720p", "1080p", "4K"])
        self.resolution.setCurrentText("1080p")
        export_form.addRow("Resolution", self.resolution)

        self.fps = QComboBox()
        self.fps.addItems(["30", "60"])
        export_form.addRow("FPS", self.fps)

        layout.addLayout(export_form)

        export_btn = QPushButton("📤 Export Video")
        export_btn.clicked.connect(self.export_video)
        layout.addWidget(export_btn)

        layout.addStretch()

    def set_video(self, path):
        self.current_video = path
        print("Properties: video set →", path)

    def apply_changes(self):
        if not self.current_video:
            QMessageBox.warning(self, "Error", "پہلے کوئی ویڈیو منتخب کریں")
            return

        speed = self.speed.value() / 100.0
        start = self.trim_start.value()
        end = self.trim_end.value()

        base = os.path.splitext(self.current_video)[0]
        output = base + "_edited.mp4"

        # Speed تبدیل کریں
        if speed != 1.0:
            ok, msg = VideoEngine.change_speed(self.current_video, output, speed)
            if not ok:
                QMessageBox.critical(self, "Error", msg)
                return

        # Trim کریں
        if end > start:
            trimmed = base + "_trimmed.mp4"
            src = output if os.path.exists(output) else self.current_video
            ok, msg = VideoEngine.trim(src, trimmed, start, end)
            if ok:
                output = trimmed
            else:
                QMessageBox.critical(self, "Error", msg)
                return

        if os.path.exists(output):
            QMessageBox.information(self, "کامیاب", f"محفوظ:\n{output}")
            self.video_processed.emit(output)
        else:
            QMessageBox.warning(self, "نوٹ", "کوئی تبدیلی لاگو نہیں ہوئی")

    def export_video(self):
        if not self.current_video:
            QMessageBox.warning(self, "Error", "پہلے کوئی ویڈیو منتخب کریں")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export Video",
            os.path.splitext(self.current_video)[0] + "_export.mp4",
            "MP4 (*.mp4)"
        )
        if not save_path:
            return

        res = self.resolution.currentText()
        fps = int(self.fps.currentText())

        QMessageBox.information(self, "براہ کرم انتظار کریں",
                                "ایکسپورٹ ہو رہی ہے... یہ کچھ وقت لے گا")

        ok, msg = VideoEngine.export(self.current_video, save_path, res, fps)
        if ok:
            QMessageBox.information(self, "کامیاب",
                                    f"ویڈیو ایکسپورٹ ہو گئی:\n{save_path}")
        else:
            QMessageBox.critical(self, "Error", msg)