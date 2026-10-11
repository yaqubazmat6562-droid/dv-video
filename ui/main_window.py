from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QSplitter, QLabel, QTabWidget,
    QFileDialog, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
import os

from ui.media_library import MediaLibrary
from ui.preview import PreviewWindow
from ui.properties import PropertiesPanel
from ui.timeline_v2 import TimelineV2
from ui.ai_panel import AIPanel
from ui.text_panel import TextPanel
from ui.filters_panel import FiltersPanel
from ui.effects_panel import EffectsPanel
from ui.mixer_panel import MixerPanel
from ui.scopes_panel import ScopesPanel
from ui.chroma_panel import ChromaPanel
from ui.subtitle_editor_panel import SubtitleEditorPanel
from ui.color_wheels_panel import ColorWheelsPanel
from ui.pro_max_panel import ProMaxPanel

from core.video_engine import VideoEngine
from core.project_io import ProjectIO
from core.auto_save import AutoSave
from core.gpu_encoder import GPUEncoder
from ui.theme_manager import Themes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DV Studio — Ultra Pro Max Video Editor")
        self.resize(1950, 1080)

        # Auto-save
        self.auto_save = AutoSave(interval=120)
        self.autosave_timer = QTimer()
        self.autosave_timer.setInterval(30000)
        self.autosave_timer.timeout.connect(self._auto_save_tick)
        self.autosave_timer.start()

        # GPU
        self.best_encoder = GPUEncoder.get_best_encoder()
        print(f"🚀 Encoder: {self.best_encoder}")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # ==================== TOP BAR ====================
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("🎬 DV Studio Ultra Pro Max"))

        top_bar.addWidget(QLabel("  Track:"))
        self.track_selector = QComboBox()
        self.track_selector.addItems(["Video 1", "Video 2", "Video 3"])
        self.track_selector.setFixedWidth(120)
        top_bar.addWidget(self.track_selector)

        top_bar.addStretch()

        gpu_label = QLabel(f"🚀 {self.best_encoder.upper()}")
        gpu_label.setStyleSheet(
            "color: #4caf50; font-weight: bold; padding: 0 10px;"
        )
        top_bar.addWidget(gpu_label)

        top_bar.addWidget(QLabel("🎨"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Purple"])
        self.theme_combo.setFixedWidth(100)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        top_bar.addWidget(self.theme_combo)

        for label, slot in [
            ("💾 Save", self.save_project),
            ("📂 Load", self.load_project),
            ("↶ Undo", self._undo),
            ("↷ Redo", self._redo),
            ("🔴 Marker", self._add_marker),
            ("🗑 Delete", self._delete_selected),
            ("📤 Export", self.export_timeline),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            top_bar.addWidget(btn)

        root.addLayout(top_bar)

        # ==================== MAIN ====================
        main_splitter = QSplitter(Qt.Horizontal)
        self.media_library = MediaLibrary()
        self.preview = PreviewWindow()

        self.right_tabs = QTabWidget()
        self.right_tabs.setStyleSheet("""
            QTabWidget::pane { background: #1e1e1e; border: 1px solid #333; }
            QTabBar::tab {
                background: #2a2a2a; color: #aaa; padding: 6px 10px;
            }
            QTabBar::tab:selected { background: #7c5cff; color: #fff; }
        """)

        # تمام Panels
        self.properties = PropertiesPanel()
        self.filters_panel = FiltersPanel()
        self.effects_panel = EffectsPanel()
        self.text_panel = TextPanel()
        self.ai_panel = AIPanel()
        self.mixer_panel = MixerPanel()
        self.scopes_panel = ScopesPanel()
        self.chroma_panel = ChromaPanel()
        self.subtitle_panel = SubtitleEditorPanel()
        self.color_wheels = ColorWheelsPanel()
        self.pro_max = ProMaxPanel()

        self.right_tabs.addTab(self.properties, "⚙️ Props")
        self.right_tabs.addTab(self.filters_panel, "🎨 Filters")
        self.right_tabs.addTab(self.color_wheels, "🎨 Color")
        self.right_tabs.addTab(self.effects_panel, "✨ Effects")
        self.right_tabs.addTab(self.text_panel, "📝 Text")
        self.right_tabs.addTab(self.ai_panel, "🤖 AI")
        self.right_tabs.addTab(self.mixer_panel, "🎛 Mixer")
        self.right_tabs.addTab(self.scopes_panel, "📊 Scopes")
        self.right_tabs.addTab(self.chroma_panel, "🟢 Chroma")
        self.right_tabs.addTab(self.subtitle_panel, "📝 SRT")
        self.right_tabs.addTab(self.pro_max, "⚡ Pro Max")

        main_splitter.addWidget(self.media_library)
        main_splitter.addWidget(self.preview)
        main_splitter.addWidget(self.right_tabs)
        main_splitter.setSizes([220, 700, 480])

        # ==================== VERTICAL ====================
        v_splitter = QSplitter(Qt.Vertical)
        v_splitter.addWidget(main_splitter)
        self.timeline = TimelineV2()
        v_splitter.addWidget(self.timeline)
        v_splitter.setSizes([560, 480])

        root.addWidget(v_splitter)

        # ==================== SIGNALS ====================
        self.media_library.media_selected.connect(self.preview.load_video)
        self.media_library.media_selected.connect(self._add_to_selected_track)
        self.media_library.media_selected.connect(self.properties.set_video)
        self.media_library.media_selected.connect(self.ai_panel.set_video)
        self.media_library.media_selected.connect(self.text_panel.set_video)
        self.media_library.media_selected.connect(self.filters_panel.set_video)
        self.media_library.media_selected.connect(self.effects_panel.set_video)
        self.media_library.media_selected.connect(self.scopes_panel.set_video)
        self.media_library.media_selected.connect(self.chroma_panel.set_video)
        self.media_library.media_selected.connect(self.subtitle_panel.set_video)
        self.media_library.media_selected.connect(self.color_wheels.set_video)
        self.media_library.media_selected.connect(self.pro_max.set_video)

        self.properties.video_processed.connect(self.preview.load_video)
        self.preview.time_updated.connect(self.timeline.set_playhead_time)
        self.timeline.time_changed.connect(self._seek_preview)

        # ==================== SHORTCUTS ====================
        QShortcut(QKeySequence("Ctrl+Z"), self, activated=self._undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, activated=self._redo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, activated=self._redo)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.save_project)
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.load_project)
        QShortcut(QKeySequence("Space"), self,
                  activated=lambda: self.preview.toggle_play())
        QShortcut(QKeySequence("Ctrl+C"), self,
                  activated=lambda: self.timeline.copy_selected())
        QShortcut(QKeySequence("Ctrl+V"), self,
                  activated=lambda: self.timeline.paste_clip())
        QShortcut(QKeySequence("Ctrl+D"), self,
                  activated=self._duplicate_selected)
        QShortcut(QKeySequence("Delete"), self,
                  activated=self._delete_selected)
        QShortcut(QKeySequence("Ctrl+M"), self,
                  activated=self._add_marker)
        QShortcut(QKeySequence("Ctrl+Shift+M"), self,
                  activated=self._clear_markers)

        self.change_theme("Dark")

    # ==================== HELPERS ====================
    def _add_to_selected_track(self, path):
        idx = self.track_selector.currentIndex() + 1
        self.timeline.add_clip_to_track(path, idx)

    def _undo(self):
        if hasattr(self.timeline, "undo"):
            self.timeline.undo()

    def _redo(self):
        if hasattr(self.timeline, "redo"):
            self.timeline.redo()

    def _delete_selected(self):
        if hasattr(self.timeline, "delete_selected"):
            self.timeline.delete_selected()

    def _duplicate_selected(self):
        if (hasattr(self.timeline, "selected_clip")
                and self.timeline.selected_clip):
            self.timeline.duplicate_clip(self.timeline.selected_clip)

    def _add_marker(self):
        if hasattr(self.timeline, "add_marker_at_playhead"):
            self.timeline.add_marker_at_playhead("Marker", "#ff3b3b")

    def _clear_markers(self):
        if hasattr(self.timeline, "clear_markers"):
            self.timeline.clear_markers()

    def _seek_preview(self, seconds):
        try:
            self.preview.player.setPosition(int(seconds * 1000))
        except Exception as e:
            print("Seek:", e)

    def _auto_save_tick(self):
        if not self.timeline:
            return
        if self.auto_save.should_save():
            state = self.timeline.get_state()
            path = self.auto_save.save(state)
            if path:
                print(f"💾 Auto-saved: {path}")

    def change_theme(self, name):
        theme = Themes.get(name)
        self.setStyleSheet(theme + """
            QTabWidget::pane { background: #1e1e1e; border: 1px solid #333; }
            QTabBar::tab {
                background: #2a2a2a; color: #aaa; padding: 6px 10px;
            }
            QTabBar::tab:selected { background: #7c5cff; color: #fff; }
            QGroupBox {
                border: 1px solid #333; border-radius: 6px;
                margin-top: 8px; padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 8px;
                padding: 0 4px; color: #7c5cff;
            }
            QSlider::groove:vertical {
                width: 4px; background: #333; border-radius: 2px;
            }
            QSlider::handle:vertical {
                background: #7c5cff; height: 12px;
                margin: 0 -4px; border-radius: 6px;
            }
            QCheckBox { color: #ccc; }
            QTableWidget {
                background: #1e1e1e; color: #ddd;
                gridline-color: #333;
            }
            QHeaderView::section {
                background: #2a2a2a; color: #aaa;
                padding: 4px; border: none;
            }
        """)

    # ==================== FILE ====================
    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "project.dvproj", "DV Project (*.dvproj)"
        )
        if not path:
            return
        state = self.timeline.get_state()
        ProjectIO.save(state, path)
        QMessageBox.information(self, "کامیاب", f"محفوظ:\n{path}")

    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "DV Project (*.dvproj)"
        )
        if not path:
            return
        data = ProjectIO.load(path)
        if data is None:
            QMessageBox.warning(self, "Error", "فائل نہیں ملی")
            return
        self.timeline.restore_state(data)
        QMessageBox.information(self, "کامیاب", "پروجیکٹ لوڈ ہو گیا")

    def export_timeline(self):
        clips = [dict(c.clip_data) for c in self.timeline.video_track.clips]
        if not clips:
            QMessageBox.warning(self, "Error", "Video Track 1 خالی ہے")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Timeline", "timeline_export.mp4", "MP4 (*.mp4)"
        )
        if not path:
            return
        QMessageBox.information(
            self, "انتظار",
            f"ایکسپورٹ ({self.best_encoder.upper()})..."
        )
        ok, msg = VideoEngine.export_timeline(clips, path)
        if ok:
            QMessageBox.information(self, "کامیاب", f"محفوظ:\n{path}")
        else:
            QMessageBox.critical(self, "Error", msg)