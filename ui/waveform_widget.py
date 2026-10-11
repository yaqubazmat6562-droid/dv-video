from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt


class WaveformWidget(QWidget):
    def __init__(self, peaks=None):
        super().__init__()
        self.peaks = peaks or []
        self.setMinimumHeight(60)
        self.setStyleSheet("background: #1f1f1f; border-radius: 4px;")

    def set_peaks(self, peaks):
        self.peaks = peaks
        self.update()

    def paintEvent(self, event):
        if not self.peaks:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        mid = h // 2

        pen = QPen(QColor("#4caf50"))
        pen.setWidth(1)
        painter.setPen(pen)

        step = w / len(self.peaks)
        for i, peak in enumerate(self.peaks):
            x = int(i * step)
            y_h = int(peak * mid * 0.9)
            painter.drawLine(x, mid - y_h, x, mid + y_h)