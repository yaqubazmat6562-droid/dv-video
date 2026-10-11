import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QLineEdit, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from core.subtitle_editor import SubtitleEditor


class SubtitleEditorPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_video = None
        self.subs = []

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📝 Subtitle Editor"))

        # Buttons
        top = QHBoxLayout()
        for label, slot in [
            ("📂 SRT کھولیں", self.load_srt),
            ("💾 محفوظ", self.save_srt),
            ("➕ نئی", self.add_row),
            ("🗑 حذف", self.delete_row),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            top.addWidget(btn)
        layout.addLayout(top)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Start (s)", "End (s)", "Text", ""]
        )
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1e1e1e; color: #ddd;
                gridline-color: #333;
            }
            QHeaderView::section {
                background: #2a2a2a; color: #aaa;
                padding: 4px; border: none;
            }
        """)
        layout.addWidget(self.table)

        self.status = QLabel("")
        layout.addWidget(self.status)

    def set_video(self, path):
        self.current_video = path

    def load_srt(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "SRT کھولیں", "", "SRT (*.srt)"
        )
        if not path:
            return
        self.subs = SubtitleEditor.parse_srt(path)
        self.refresh_table()
        self.status.setText(f"✅ {len(self.subs)} سب ٹائٹلز لوڈ ہو گئے")

    def save_srt(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "SRT محفوظ", "subtitle.srt", "SRT (*.srt)"
        )
        if not path:
            return
        self.collect_from_table()
        SubtitleEditor.save_srt(self.subs, path)
        self.status.setText(f"✅ محفوظ: {path}")

    def add_row(self):
        self.subs.append({"index": len(self.subs) + 1,
                          "start": 0.0, "end": 2.0, "text": ""})
        self.refresh_table()

    def delete_row(self):
        r = self.table.currentRow()
        if r >= 0:
            self.subs.pop(r)
            self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.subs))
        for i, s in enumerate(self.subs):
            self.table.setItem(i, 0, QTableWidgetItem(str(s["start"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(s["end"])))
            self.table.setItem(i, 2, QTableWidgetItem(s["text"]))

    def collect_from_table(self):
        for i in range(self.table.rowCount()):
            try:
                self.subs[i]["start"] = float(self.table.item(i, 0).text())
                self.subs[i]["end"] = float(self.table.item(i, 1).text())
                self.subs[i]["text"] = self.table.item(i, 2).text()
            except Exception:
                pass