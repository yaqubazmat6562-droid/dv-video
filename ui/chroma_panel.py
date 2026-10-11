import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QSlider, QFileDialog,
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
from core.chroma_key import ChromaKey


class ChromaPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_video = None
        self.bg_path = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🟢 Chroma Key (Green Screen)"))

        box = QGroupBox("Settings")
        v = QVBoxLayout(box)

        v.addWidget(QLabel("Key Color:"))
        self.color = QComboBox()
        self.color.addItems(list(ChromaKey.COLORS.keys()))
        v.addWidget(self.color)

        v.addWidget(QLabel("Similarity:"))
        self.similarity = QSlider(Qt.Horizontal)
        self.similarity.setRange(10, 50)
        self.similarity.setValue(30)
        v.addWidget(self.similarity)

        v.addWidget(QLabel("Edge Blend:"))
        self.blend = QSlider(Qt.Horizontal)
        self.blend.setRange(0, 30)
        self.blend.setValue(10)
        v.addWidget(self.blend)

        layout.addWidget(box)

        # نئی بیک گراؤنڈ
        layout.addWidget(QLabel("نئی بیک گراؤنڈ (اختیاری):"))
        pick_btn = QPushButton("🖼 بیک گراؤنڈ منتخب کریں")
        pick_btn.clicked.connect(self.pick_bg)
        layout.addWidget(pick_btn)

        self.bg_label = QLabel("کوئی نہیں (خالی webm)")
        self.bg_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.bg_label)

        apply_btn = QPushButton("✅ Chroma Key لگائیں")
        apply_btn.clicked.connect(self.apply)
        layout.addWidget(apply_btn)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch()

    def set_video(self, path):
        self.current_video = path
        self.status.setText(f"📹 {os.path.basename(path)}")

    def pick_bg(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Background", "",
            "Media (*.mp4 *.mov *.png *.jpg)"
        )
        if path:
            self.bg_path = path
            self.bg_label.setText(os.path.basename(path))

    def apply(self):
        if not self.current_video:
            QMessageBox.warning(self, "Error", "پہلے ویڈیو منتخب کریں")
            return

        ext = ".webm" if not self.bg_path else ".mp4"
        output = os.path.splitext(self.current_video)[0] + "_chroma" + ext

        QMessageBox.information(self, "انتظار", "Chroma Key ہو رہی ہے...")

        ok, msg = ChromaKey.remove_background(
            self.current_video, output,
            bg_video_or_image=self.bg_path,
            color=self.color.currentText(),
            similarity=self.similarity.value() / 100.0,
            blend=self.blend.value() / 100.0,
        )

        if ok:
            self.status.setText(f"✅ محفوظ: {output}")
            QMessageBox.information(self, "کامیاب",
                                    f"محفوظ:\n{output}")
        else:
            self.status.setText(f"❌ {msg}")
            QMessageBox.critical(self, "Error", msg)