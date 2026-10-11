import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from core.text_overlay import TextOverlay


class TextPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_video = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📝 Text Overlay"))

        # ٹیکسٹ ان پٹ
        layout.addWidget(QLabel("Text:"))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("یہاں ٹیکسٹ لکھیں...")
        layout.addWidget(self.text_input)

        # پوزیشن
        layout.addWidget(QLabel("Position:"))
        self.position = QComboBox()
        self.position.addItems(list(TextOverlay.POSITIONS.keys()))
        self.position.setCurrentText("نیچے")
        layout.addWidget(self.position)

        # رنگ
        layout.addWidget(QLabel("Color:"))
        self.color = QComboBox()
        self.color.addItems(list(TextOverlay.COLORS.keys()))
        self.color.setCurrentText("سفید")
        layout.addWidget(self.color)

        # سائز
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Size:"))
        self.size = QSpinBox()
        self.size.setRange(12, 200)
        self.size.setValue(48)
        size_row.addWidget(self.size)
        layout.addLayout(size_row)

        # وقت (start/end)
        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("Start:"))
        self.start = QSpinBox()
        self.start.setRange(0, 99999)
        self.start.setSuffix(" s")
        time_row.addWidget(self.start)

        time_row.addWidget(QLabel("End:"))
        self.end = QSpinBox()
        self.end.setRange(0, 99999)
        self.end.setSuffix(" s")
        time_row.addWidget(self.end)
        layout.addLayout(time_row)

        # بیک گراؤنڈ باکس
        self.bg_box = QCheckBox("پس منظر سیاہ باکس")
        self.bg_box.setChecked(False)
        layout.addWidget(self.bg_box)

        layout.addSpacing(10)

        # بٹن
        apply_btn = QPushButton("✅ Text شامل کریں")
        apply_btn.clicked.connect(self.apply_text)
        layout.addWidget(apply_btn)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        layout.addStretch()

    def set_video(self, path):
        self.current_video = path
        self.status.setText(f"📹 {os.path.basename(path)}")

    def apply_text(self):
        if not self.current_video:
            QMessageBox.warning(self, "Error", "پہلے ویڈیو منتخب کریں")
            return

        text = self.text_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Error", "پہلے ٹیکسٹ لکھیں")
            return

        output = os.path.splitext(self.current_video)[0] + "_text.mp4"

        self.status.setText("⏳ ٹیکسٹ لگایا جا رہا ہے...")

        ok, msg = TextOverlay.add_text(
            self.current_video,
            output,
            text=text,
            position=self.position.currentText(),
            color=self.color.currentText(),
            font_size=self.size.value(),
            start=self.start.value(),
            end=self.end.value() if self.end.value() > 0 else None,
            bg_box=self.bg_box.isChecked(),
        )

        if ok:
            self.status.setText(f"✅ محفوظ: {output}")
            QMessageBox.information(self, "کامیاب",
                                    f"ٹیکسٹ لگا دیا گیا:\n{output}")
        else:
            self.status.setText(f"❌ {msg}")
            QMessageBox.critical(self, "Error", msg)