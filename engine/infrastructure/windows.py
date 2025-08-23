import os
import sys
import random
from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtCore import (
    Qt,
    QUrl,
    Signal,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    Property,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QScrollArea,
    QGroupBox,
    QFrame,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtGui import QFont

from engine.infrastructure.widgets import SoundSection


class MusicBoardMainWindow(QMainWindow):
    """Main window for the music board application."""

    def __init__(self) -> None:
        super().__init__()
        self.sections: List[SoundSection] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the main window UI."""
        self.setWindowTitle("🎛️ OpenBoard - Professional Audio Mixer")
        self.setGeometry(100, 100, 1400, 900)

        # Modern styling
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """
        )

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
        ambient_section = SoundSection("🌿 AMBIENT", "ambient", loop_mode=True)
        music_section = SoundSection("🎵 MUSIC", "music", loop_mode=True)
        effects_section = SoundSection(
            "⚡ EFFECTS", "effects", loop_mode=False
        )

        self.sections = [ambient_section, music_section, effects_section]

        # Add sections to layout with equal spacing
        for section in self.sections:
            section.setStyleSheet(
                """
                SoundSection {
                    background-color: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 12px;
                }
            """
            )
            sections_layout.addWidget(section, 1)  # Equal stretch factor

        main_layout.addLayout(sections_layout)

    def _create_header(self, main_layout: QVBoxLayout) -> None:
        """Create the header with master controls."""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 16px;
            }
        """
        )
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(24, 16, 24, 16)

        # Title with icon
        title_label = QLabel("🎛️ OpenBoard")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet(
            """
            QLabel {
                color: white;
            }
        """
        )
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Master volume section
        volume_container = QWidget()
        volume_layout = QHBoxLayout(volume_container)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(12)

        master_vol_label = QLabel("Master Volume:")
        master_vol_label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
        """
        )
        volume_layout.addWidget(master_vol_label)

        self.master_volume_slider = QSlider(Qt.Horizontal)
        self.master_volume_slider.setRange(0, 100)
        self.master_volume_slider.setValue(80)
        self.master_volume_slider.setFixedWidth(180)
        self.master_volume_slider.valueChanged.connect(
            self._on_master_volume_changed
        )
        self.master_volume_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #34495e;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #95a5a6, stop:1 #7f8c8d);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #3498db, stop:1 #2980b9);
                border: 2px solid white;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2980b9, stop:1 #21618c);
            }
        """
        )
        volume_layout.addWidget(self.master_volume_slider)

        self.master_volume_label = QLabel("80%")
        self.master_volume_label.setFixedWidth(40)
        self.master_volume_label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
        """
        )
        volume_layout.addWidget(self.master_volume_label)

        header_layout.addWidget(volume_container)

        # Stop all button
        stop_all_button = QPushButton("⏹ Stop All")
        stop_all_button.setFixedSize(120, 48)
        stop_all_button.clicked.connect(self._stop_all_sounds)
        stop_all_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                border-radius: 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                   stop:0 #c0392b, stop:1 #a93226);
                border: 2px solid #fff;
            }
            QPushButton:pressed {
                background: #a93226;
            }
        """
        )

        header_layout.addWidget(stop_all_button)

        main_layout.addWidget(header_widget)

    def _on_master_volume_changed(self, value: int) -> None:
        """Handle master volume slider changes."""
        volume_percent = value / 100.0
        self.master_volume_label.setText(f"{value}%")

        # Update all sections
        for section in self.sections:
            section.set_master_volume(volume_percent)

    def _stop_all_sounds(self) -> None:
        """Stop all sounds in all sections."""
        for section in self.sections:
            section.stop_all()
