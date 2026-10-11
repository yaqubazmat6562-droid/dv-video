import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QSlider, QGroupBox, QHBoxLayout, QMessageBox,
    QFileDialog
)
from PySide6.QtCore import Qt
from core.lut_loader import LUTLoader, ColorWheels


class ColorWheelsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_video = None
        self.lut_path = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🎨 Color Grading Ultra"))

        # ---------- LUT ----------
        box = QGroupBox("Cinema LUT (.cube)")
        v = QVBoxLayout(box)

        pick_btn = QPushButton("📁 LUT منتخب کریں")
        pick_btn.clicked.connect(self.pick_lut)
        v.addWidget(pick_btn)

        self.lut_label = QLabel("کوئی LUT نہیں")
        self.lut_label.setStyleSheet("color: #888; font-size: 10px;")
        v.addWidget(self.lut_label)

        v.addWidget(QLabel("Intensity:"))
        self.lut_intensity = QSlider(Qt.Horizontal)
        self.lut_intensity.setRange(0, 100)
        self.lut_intensity.setValue(100)
        v.addWidget(self.lut_intensity)

        apply_lut = QPushButton("✅ LUT لگائیں")
        apply_lut.clicked.connect(self.apply_lut)
        v.addWidget(apply_lut)

        layout.addWidget(box)

        # ---------- Color Wheels ----------
        box2 = QGroupBox("Lift / Gamma / Gain")
        v2 = QVBoxLayout(box2)

        self.sliders = {}
        for name, default in [("lift_r", 0), ("lift_g", 0), ("lift_b", 0),
                              ("gamma_r", 100), ("gamma_g", 100),
                              ("gamma_b", 100),
                              ("gain_r", 100), ("gain_g", 100),
                              ("gain_b", 100)]:
            row = QHBoxLayout()
            row.addWidget(QLabel(name.replace("_", " ").title()))
            s = QSlider(Qt.Horizontal)
            s.setRange(-100 if "lift" in name else 0, 200)
            s.setValue(default)
            row.addWidget(s)
            self.sliders[name] = s
            v2.addLayout(row)

        reset_btn = QPushButton("↺ Reset")
        reset_btn.clicked.connect(self.reset_wheels)
        v2.addWidget(reset_btn)

        apply_cc = QPushButton("✅ Color Correction لگائیں")
        apply_cc.clicked.connect(self.apply_color)
        v2.addWidget(apply_cc)

        layout.addWidget(box2)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch()

    def set_video(self, path):
        self.current_video = path
        self.status.setText(f"📹 {os.path.basename(path)}")

    def pick_lut(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "LUT منتخب کریں", "", "LUT Files (*.cube)"
        )
        if path:
            self.lut_path = path
            self.lut_label.setText(os.path.basename(path))

    def reset_wheels(self):
        for name, s in self.sliders.items():
            s.setValue(0 if "lift" in name else 100)

    def apply_lut(self):
        if not self.current_video:
            QMessageBox.warning(self, "Error", "پہلے ویڈیو منتخب کریں")
            return
        if not self.lut_path:
            QMessageBox.warning(self, "Error", "پہلے LUT منتخب کریں")
            return

        output = os.path.splitext(self.current_video)[0] + "_lut.mp4"
        ok, msg = LUTLoader.apply(
            self.current_video, output, self.lut_path,
            intensity=self.lut_intensity.value() / 100.0
        )
        if ok:
            self.status.setText(f"✅ محفوظ: {output}")
            QMessageBox.information(self, "کامیاب", f"محفوظ:\n{output}")
        else:
            self.status.setText(f"❌ {msg}")
            QMessageBox.critical(self, "Error", msg)

    def apply_color(self):
        if not self.current_video:
            QMessageBox.warning(self, "Error", "پہلے ویڈیو منتخب کریں")
            return
        output = os.path.splitext(self.current_video)[0] + "_cc.mp4"
        ok, msg = ColorWheels.apply(
            self.current_video, output,
            lift_r=self.sliders["lift_r"].value() / 100.0,
            lift_g=self.sliders["lift_g"].value() / 100.0,
            lift_b=self.sliders["lift_b"].value() / 100.0,
            gamma_r=self.sliders["gamma_r"].value() / 100.0,
            gamma_g=self.sliders["gamma_g"].value() / 100.0,
            gamma_b=self.sliders["gamma_b"].value() / 100.0,
            gain_r=self.sliders["gain_r"].value() / 100.0,
            gain_g=self.sliders["gain_g"].value() / 100.0,
            gain_b=self.sliders["gain_b"].value() / 100.0,
        )
        if ok:
            self.status.setText(f"✅ محفوظ: {output}")
            QMessageBox.information(self, "کامیاب", f"محفوظ:\n{output}")
        else:
            self.status.setText(f"❌ {msg}")
            QMessageBox.critical(self, "Error", msg)