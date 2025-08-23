"""
PySide6 Music Board Application
A three-section music player for ambient, music, and effects folders.
"""

import os
import sys
import random
from pathlib import Path
from typing import List

from PySide6.QtCore import (
    Qt,
    QUrl,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
    Property,
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QScrollArea,
    QFrame,
)
from PySide6.QtGui import QFont

from engine.infrastructure.audio_service import QtAudioService
from engine.infrastructure.repository import FileSystemSoundRepository
from engine.infrastructure.windows import MusicBoardMainWindow


def create_sample_folders() -> None:
    """Create sound folders if they don't exist."""

    folders = ["ambient", "music", "effects"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

        # Create a readme file in each folder
        readme_path = os.path.join(folder, "README.txt")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as f:
                f.write(f"{folder.upper()} SOUNDS\n")
                f.write("=" * 30 + "\n\n")
                f.write(f"Place your {folder} audio files here.\n\n")
                f.write("Supported formats: MP3, WAV, OGG, M4A, FLAC, AAC\n\n")
                if folder in ["ambient", "music"]:
                    f.write("Files in this folder will loop automatically.\n")
                else:
                    f.write(
                        "Files in this folder will play once at full volume immediately.\n"
                    )
                    f.write(
                        "You can also add folders containing multiple sounds for random playback!\n"
                    )
                    f.write(
                        "Each time you click play on a folder, a random sound from that folder will play.\n"
                    )
                f.write(
                    "\nUse individual volume sliders and master volume for perfect mixing.\n"
                )
                f.write(
                    "Files and folders are automatically sorted in alphabetical order.\n"
                )


def main() -> int:
    """Main application entry point."""

    app = QApplication(sys.argv)
    app.setApplicationName("OpenBoard Audio Mixer")
    app.setApplicationVersion("1.0.0")

    app.setStyle('Fusion')

    create_sample_folders()

    audio_service = QtAudioService()
    repository = FileSystemSoundRepository()
    window = MusicBoardMainWindow(
        audio_service=audio_service, repository=repository
    )
    window.show()

    # Start the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
