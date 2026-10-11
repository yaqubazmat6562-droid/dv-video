class Themes:
    DARK = """
        QMainWindow { background: #1a1a1a; }
        QLabel { color: #ddd; }
        QPushButton {
            background: #3a3a3a; color: #fff;
            padding: 6px 12px; border-radius: 6px;
        }
        QPushButton:hover { background: #4a4a4a; }
        QListWidget, QComboBox, QSpinBox, QLineEdit {
            background: #222; color: #ddd;
            border: 1px solid #333; border-radius: 6px;
            padding: 4px;
        }
        QSlider::groove:horizontal {
            height: 4px; background: #333; border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #7c5cff; width: 12px;
            margin: -4px 0; border-radius: 6px;
        }
        QSplitter::handle { background: #2a2a2a; }
    """

    LIGHT = """
        QMainWindow { background: #f5f5f5; }
        QLabel { color: #222; }
        QPushButton {
            background: #e0e0e0; color: #222;
            padding: 6px 12px; border-radius: 6px;
        }
        QPushButton:hover { background: #d0d0d0; }
        QListWidget, QComboBox, QSpinBox, QLineEdit {
            background: #fff; color: #222;
            border: 1px solid #ccc; border-radius: 6px;
            padding: 4px;
        }
        QSlider::groove:horizontal {
            height: 4px; background: #ccc; border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #7c5cff; width: 12px;
            margin: -4px 0; border-radius: 6px;
        }
        QSplitter::handle { background: #ddd; }
    """

    PURPLE = """
        QMainWindow { background: #1a0f2e; }
        QLabel { color: #e0d5ff; }
        QPushButton {
            background: #4a2d7a; color: #fff;
            padding: 6px 12px; border-radius: 6px;
        }
        QPushButton:hover { background: #5a3d8a; }
        QListWidget, QComboBox, QSpinBox, QLineEdit {
            background: #2a1a4a; color: #e0d5ff;
            border: 1px solid #4a2d7a; border-radius: 6px;
            padding: 4px;
        }
        QSlider::handle:horizontal {
            background: #b088ff; width: 12px;
            margin: -4px 0; border-radius: 6px;
        }
        QSplitter::handle { background: #2a1a4a; }
    """

    @staticmethod
    def get(name):
        return {"Dark": Themes.DARK,
                "Light": Themes.LIGHT,
                "Purple": Themes.PURPLE}.get(name, Themes.DARK)