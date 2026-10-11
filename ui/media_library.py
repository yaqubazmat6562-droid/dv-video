from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFileDialog, QLabel, QListWidgetItem
)
from PySide6.QtCore import Signal


class MediaLibrary(QWidget):
    # سگنل: جب ویڈیو منتخب ہو
    media_selected = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📁 Media Library"))

        self.upload_btn = QPushButton("Upload Media")
        self.upload_btn.clicked.connect(self.import_media)
        layout.addWidget(self.upload_btn)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_click)
        layout.addWidget(self.list_widget)

    def import_media(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Media",
            "", "Media Files (*.mp4 *.mov *.mkv *.mp3 *.wav *.png *.jpg)"
        )
        for f in files:
            item = QListWidgetItem(f"🎬 {f.split('/')[-1]}")
            item.setData(1000, f)   # اصل پاتھ محفوظ
            self.list_widget.addItem(item)

    def on_item_double_click(self, item):
        path = item.data(1000)
        if path:
            self.media_selected.emit(path)