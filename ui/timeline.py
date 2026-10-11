from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
)


class Timeline(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("🕒 Timeline"))

        self.clip_list = QListWidget()
        self.clip_list.setStyleSheet(
            "background:#1e1e1e; color:#ccc; border-radius:6px;"
        )
        self.clip_list.setMaximumHeight(180)
        layout.addWidget(self.clip_list)

    def add_clip(self, path):
        name = path.split("/")[-1]
        item = QListWidgetItem(f"🎞 {name}")
        self.clip_list.addItem(item)