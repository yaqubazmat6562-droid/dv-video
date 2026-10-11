from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QTimer
from core.scopes import Scopes


class ScopesPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_video = None
        self.hist_data = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("📊 Scopes"))

        self.canvas = HistogramCanvas()
        layout.addWidget(self.canvas)

        btn = QPushButton("🔄 Refresh Scopes")
        btn.clicked.connect(self.refresh)
        layout.addWidget(btn)

        self.status = QLabel("")
        self.status.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self.status)

        layout.addStretch()

        # Auto-refresh
        self.timer = QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()

    def set_video(self, path):
        self.current_video = path
        self.refresh()

    def refresh(self):
        if not self.current_video:
            return
        # پلے ہیڈ کا ٹائم لیں (اگر ملے)
        time = 0
        png = Scopes.grab_frame(self.current_video, time=time)
        if png:
            hist = Scopes.compute_histogram(png)
            if hist:
                self.hist_data = hist
                self.canvas.set_data(hist)
                self.status.setText("✅ تازہ")


class HistogramCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.data = None
        self.setMinimumHeight(200)
        self.setStyleSheet("background: #111; border-radius: 6px;")

    def set_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        if not self.data:
            painter.setPen(QColor("#555"))
            painter.drawText(self.rect(), Qt.AlignCenter, "No Data")
            return

        # Grid
        painter.setPen(QPen(QColor("#222"), 1))
        for i in range(1, 4):
            y = i * h // 4
            painter.drawLine(0, y, w, y)

        # RGB
        colors = {"r": QColor(255, 80, 80, 180),
                  "g": QColor(80, 255, 80, 180),
                  "b": QColor(80, 80, 255, 180)}

        for key, color in colors.items():
            hist = self.data[key]
            max_val = max(hist.max(), 1)
            points = []

            for i, v in enumerate(hist):
                x = int(i * w / len(hist))
                y = int(h - (v / max_val) * h * 0.9)
                points.append((x, y))

            painter.setPen(QPen(color, 1))
            for i in range(len(points) - 1):
                painter.drawLine(points[i][0], points[i][1],
                                 points[i+1][0], points[i+1][1])