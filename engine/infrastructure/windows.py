from pathlib import Path
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from engine.infrastructure.services import QtAudioService
from engine.infrastructure.widgets import SoundSection, colored_svg

ICON_DIR = Path(__file__).resolve().parent / "icons" / "svgs" / "solid"


class MusicBoardMainWindow(QMainWindow):
    """Main window for the music board application."""

    def __init__(self) -> None:
        super().__init__()
        self.sections: List[SoundSection] = []
        self.audio_service = QtAudioService()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the main window UI."""

        self.setWindowTitle("OpenBoard - TTRPG Audio Mixer and Soundboard")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header with master controls
        self._create_header(main_layout)

        # Three sections layout
        sections_layout = QHBoxLayout()
        sections_layout.setSpacing(20)

        # Create the three sections
        ambient_section = SoundSection(
            "AMBIENT", "ambient", self.audio_service, loop_mode=True
        )
        music_section = SoundSection(
            "MUSIC", "music", self.audio_service, loop_mode=True
        )
        effects_section = SoundSection(
            "EFFECTS", "effects", self.audio_service, loop_mode=False
        )

        self.sections = [ambient_section, music_section, effects_section]

        # Add sections to layout with equal spacing
        for section in self.sections:
            sections_layout.addWidget(section, 1)  # Equal stretch factor

        main_layout.addLayout(sections_layout)

    def _create_header(self, main_layout: QVBoxLayout) -> None:
        """Create the header with master controls."""

        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setObjectName("headerWidget")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(24, 16, 24, 16)

        # Title with colored icon
        slider_pix = colored_svg("sliders.svg", "#4CAF50", 24)
        self.setWindowIcon(QIcon(slider_pix))
        icon_label = QLabel()
        icon_label.setPixmap(slider_pix)
        title_label = QLabel("OpenBoard")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setObjectName("titleLabel")

        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        header_layout.addWidget(title_container)

        header_layout.addStretch()

        # Master volume section
        volume_container = QWidget()
        volume_layout = QHBoxLayout(volume_container)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(12)

        master_vol_label = QLabel("Master Volume:")
        master_vol_label.setObjectName("masterVolLabel")
        volume_layout.addWidget(master_vol_label)

        self.master_volume_slider = QSlider(Qt.Horizontal)
        self.master_volume_slider.setRange(0, 100)
        self.master_volume_slider.setValue(80)
        self.master_volume_slider.setFixedWidth(180)
        self.master_volume_slider.valueChanged.connect(
            self._on_master_volume_changed
        )
        self.master_volume_slider.setObjectName("masterVolumeSlider")
        volume_layout.addWidget(self.master_volume_slider)

        self.master_volume_label = QLabel("80%")
        self.master_volume_label.setFixedWidth(40)
        self.master_volume_label.setObjectName("masterVolumeValue")
        volume_layout.addWidget(self.master_volume_label)

        header_layout.addWidget(volume_container)

        # Refresh and Stop All buttons
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon(str(ICON_DIR / "refresh.svg")))
        refresh_button.setFixedSize(120, 48)
        refresh_button.clicked.connect(self._refresh_all_sections)
        refresh_button.setObjectName("refreshButton")
        header_layout.addWidget(refresh_button)

        stop_all_button = QPushButton("Stop All")
        stop_all_button.setIcon(QIcon(colored_svg("stop.svg", "#4CAF50", 24)))
        stop_all_button.setFixedSize(120, 48)
        stop_all_button.clicked.connect(self._stop_all_sounds)
        stop_all_button.setObjectName("stopAllButton")
        header_layout.addWidget(stop_all_button)

        main_layout.addWidget(header_widget)

    def _on_master_volume_changed(self, value: int) -> None:
        """Handle master volume slider changes."""

        volume_percent = value / 100.0
        self.master_volume_label.setText(f"{value}%")
        self.audio_service.set_master_volume(volume_percent)

    def _stop_all_sounds(self) -> None:
        """Stop all sounds in all sections."""

        for section in self.sections:
            section.stop_all()

    def _refresh_all_sections(self) -> None:
        """Refresh sound lists for all sections."""

        for section in self.sections:
            section.refresh()
