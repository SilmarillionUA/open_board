import os
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
)

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

    app.setStyle('Fusion')

    # Load global stylesheet
    style_path = Path(__file__).resolve().parent / "engine" / "infrastructure" / "style.qss"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    create_sample_folders()

    window = MusicBoardMainWindow()
    window.show()

    # Start the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
