import os
import csv
import shutil
from pathlib import Path
from typing import Callable, List, Optional

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from engine.application.services import AudioService
from engine.domain.sound import Sound, SoundFolder

ICON_DIR = Path(__file__).resolve().parent / "icons" / "svgs" / "solid"


def colored_svg(name: str, color: str, size: int) -> QPixmap:
    """Return a tinted pixmap for the given SVG icon."""

    pixmap = QIcon(str(ICON_DIR / name)).pixmap(size, size)
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return pixmap


def resolve_youtube(url: str) -> tuple[str, str]:
    """Return direct audio stream URL and title for a YouTube link."""
    from pytube import YouTube

    yt = YouTube(url)
    stream = (
        yt.streams
        .filter(only_audio=True, mime_type="audio/mp4")
        .order_by("abr")
        .desc()
        .first()
    )
    if stream is None:
        stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    if stream is None:
        raise ValueError("No audio stream found")
    return stream.url, yt.title


class SoundPlayer(QWidget):
    """Individual sound player widget with play/stop and volume controls."""

    def __init__(
        self,
        file_path: str,
        loop_mode: bool = False,
        is_folder: bool = False,
        service: Optional[AudioService] = None,
        parent: Optional[QWidget] = None,
        *,
        is_stream: bool = False,
        display_name: Optional[str] = None,
    ) -> None:
        super().__init__(parent)
        self.file_path = file_path
        self.loop_mode = loop_mode
        self.is_folder = is_folder
        self.is_stream = is_stream
        self._service = service
        self._stream_resolved = stream_resolved

        if self.is_folder:
            self.sound_folder = SoundFolder(Path(file_path))
            self.sound_folder.scan()
            self.filename = Path(file_path).name
            self.sound: Optional[Sound] = None
        elif self.is_stream:
            self.sound = Sound(file_path, loop_mode)
            self.filename = display_name or file_path
        else:
            self.sound = Sound(Path(file_path), loop_mode)
            self.filename = self.sound.path.stem

        self._setup_ui()

        if self._service:
            self._service.playback_finished.connect(self._on_playback_finished)
        self._fade_timer: Optional[QTimer] = None
        self._fade_start: float = 0.0
        self._fade_end: float = 0.0
        self._fade_elapsed: int = 0
        self._fade_callback: Optional[Callable[[], None]] = None

    def _start_playback(self) -> None:
        """Trigger playback via the audio service."""
        if self.sound and self._service:
            if self.is_stream:
                try:
                    new_url, new_title = resolve_youtube(self.file_path)
                except Exception:
                    return
                self.filename = new_title
                self.name_label.setText(self.filename)
                self.sound = Sound(new_url, self.loop_mode)
            self._stop_fade()
            if self.loop_mode:
                self._service.set_sound_volume(self.sound, 0.0)
            self._service.play_sound(self.sound)
            if self.loop_mode:

                self._start_fade(0.0, self.volume_slider.value() / 100.0)
            else:
                self._service.set_sound_volume(
                    self.sound, self.volume_slider.value() / 100.0
                )

    def _start_fade(
        self,
        start: float,
        end: float,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Start a fade from ``start`` to ``end`` over 3 seconds."""

        if not (self.sound and self._service):
            return
        self._stop_fade()
        self._fade_start = start
        self._fade_end = end
        self._fade_elapsed = 0
        self._fade_callback = callback
        self._service.set_sound_volume(self.sound, start)
        self._fade_timer = QTimer(self)
        self._fade_timer.timeout.connect(self._fade_step)
        self._fade_timer.start(100)

    def _fade_step(self) -> None:
        if not (self.sound and self._service and self._fade_timer):
            return
        self._fade_elapsed += 100
        ratio = min(self._fade_elapsed / 3000, 1.0)
        volume = self._fade_start + (self._fade_end - self._fade_start) * ratio
        self._service.set_sound_volume(self.sound, volume)
        if ratio >= 1.0:
            callback = self._fade_callback
            self._stop_fade()
            if callback:
                callback()

    def _stop_fade(self) -> None:
        if self._fade_timer:
            self._fade_timer.stop()
            self._fade_timer.deleteLater()
            self._fade_timer = None
        self._fade_callback = None

    def _setup_ui(self) -> None:
        """Set up the player UI."""
        self.setMinimumHeight(80)
        self.setMaximumHeight(80)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(4)

        # Top row: Sound name with folder icon if applicable
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Sound name with folder indicator
        name_text = self.filename
        if self.is_folder:
            folder_icon = (ICON_DIR / "folder.svg").as_posix()
            repeat_icon = (ICON_DIR / "repeat.svg").as_posix()
            folder_html = (
                f"<img src='{folder_icon}' width='14' height='14' "
                "style='vertical-align: middle;'/> "
            )
            repeat_html = (
                f"<img src='{repeat_icon}' width='14' height='14' "
                "style='vertical-align: middle;'/>"
            )
            name_text = f"{folder_html}{self.filename} {repeat_html}"

        self.name_label = QLabel()
        self.name_label.setTextFormat(Qt.RichText)
        self.name_label.setText(name_text)
        self.name_label.setWordWrap(True)
        self.name_label.setObjectName("playerNameLabel")
        top_layout.addWidget(self.name_label, 1)

        main_layout.addLayout(top_layout)

        # Bottom row: Controls + Volume (in one line)
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(6)

        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon(colored_svg("play.svg", "#4CAF50", 14)))
        self.play_button.setIconSize(QSize(14, 14))
        self.play_button.setFixedSize(20, 20)
        self.play_button.clicked.connect(self.play)
        self.play_button.setObjectName("playButton")
        bottom_layout.addWidget(self.play_button)

        self.pause_button = QPushButton()
        self.pause_button.setIcon(
            QIcon(colored_svg("pause.svg", "#ffcc00", 14))
        )
        self.pause_button.setIconSize(QSize(14, 14))
        self.pause_button.setFixedSize(20, 20)
        self.pause_button.clicked.connect(self._pause)
        self.pause_button.setObjectName("pauseButton")
        self.pause_button.hide()
        bottom_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon(colored_svg("stop.svg", "#CC0202", 14)))
        self.stop_button.setIconSize(QSize(14, 14))
        self.stop_button.setFixedSize(20, 20)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setObjectName("stopButton")
        bottom_layout.addWidget(self.stop_button)

        # Volume controls (inline)
        vol_label = QLabel("Vol:")
        vol_label.setObjectName("volumeTextLabel")
        bottom_layout.addWidget(vol_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedHeight(16)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        self.volume_slider.setObjectName("volumeSlider")
        bottom_layout.addWidget(self.volume_slider, 1)

        self.volume_label = QLabel("70%")
        self.volume_label.setFixedWidth(30)
        self.volume_label.setObjectName("volumeValueLabel")
        bottom_layout.addWidget(self.volume_label)

        main_layout.addLayout(bottom_layout)

        # Add folder info if this is a folder
        if self.is_folder:
            info_label = QLabel(f"({len(self.sound_folder.sounds)} sounds)")
            info_label.setObjectName("folderInfoLabel")
            main_layout.addWidget(info_label)

    def play(self) -> None:
        """Start playing the sound via the audio service."""

        if self.is_folder:
            random_sound = self.sound_folder.random_sound()
            if random_sound is None:
                return
            self.sound = Sound(random_sound.path, self.loop_mode)
        if self.sound and self._service:
            self._start_playback()
        self.play_button.hide()
        self.pause_button.show()

    def _pause(self) -> None:
        """Fade out and pause, remembering the pressed position."""

        if self.sound and self._service:
            position = self._service.get_sound_position(self.sound)
            if self._fade_timer:
                ratio = min(self._fade_elapsed / 3000, 1.0)
                current = (
                    self._fade_start
                    + (self._fade_end - self._fade_start) * ratio
                )
            else:
                current = self.volume_slider.value() / 100.0
            
            def finish(s=self.sound, pos=position) -> None:
                self._service.pause_sound(s)
                self._service.set_sound_position(s, pos)
                self.pause_button.hide()
                self.play_button.show()

            self._start_fade(current, 0.0, finish)
        else:
            self._stop_fade()
            self.pause_button.hide()
            self.play_button.show()

    def stop(self) -> None:
        """Stop playback immediately and reset position."""

        self._stop_fade()
        if self.sound and self._service:
            self._service.stop_sound(self.sound)
        self.pause_button.hide()
        self.play_button.show()

    def _on_volume_changed(self, value: int) -> None:
        """Handle volume slider changes."""

        self.volume_label.setText(f"{value}%")
        if self.sound and self._service:
            self._service.set_sound_volume(self.sound, value / 100.0)

    def _on_playback_finished(self, sound: Sound) -> None:
        """Reset controls when the current sound finishes playing."""
        if self.sound == sound:
            self._stop_fade()
            self.pause_button.hide()
            self.play_button.show()


class SoundSection(QWidget):
    """A section containing multiple sound players."""

    def __init__(
        self,
        title: str,
        folder_path: str,
        service: AudioService,
        loop_mode: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.title = title
        self.folder_path = folder_path
        self.loop_mode = loop_mode
        self._service = service
        self.players: List[SoundPlayer] = []

        self._setup_ui()
        self._load_sounds()

    def _setup_ui(self) -> None:
        """Set up the section UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Section header with colored icon
        if "AMBIENT" in self.title:
            icon_file = "leaf.svg"
            header_color = "#4CAF50"
        elif "MUSIC" in self.title:
            icon_file = "music.svg"
            header_color = "#2196F3"
        else:
            icon_file = "bolt.svg"
            header_color = "#FF9800"

        header = QWidget()
        header.setObjectName("sectionHeader")
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 0, 12, 0)
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_label.setPixmap(colored_svg(icon_file, header_color, 24))
        header_layout.addWidget(icon_label)

        text_label = QLabel(self.title)
        text_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(text_label)

        header.setStyleSheet(
            f"""
            #sectionHeader {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {header_color},
                    stop:1 {self._darken_color(header_color)}
                );
                border-radius: 12px 12px 0 0;
            }}
            #sectionHeader QLabel {{
                color: white;
                font-size: 16px;
                font-weight: bold;
            }}
        """
        )
        layout.addWidget(header)

        # Scroll area for sound players
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setObjectName("sectionScrollArea")

        self.players_widget = QWidget()
        self.players_widget.setObjectName("playersWidget")
        self.players_layout = QVBoxLayout(self.players_widget)
        self.players_layout.setContentsMargins(8, 8, 8, 8)
        self.players_layout.setSpacing(6)

        scroll_area.setWidget(self.players_widget)
        layout.addWidget(scroll_area)

        # Bottom buttons for adding sounds
        button_row = QWidget()
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(8, 4, 8, 4)
        button_layout.setSpacing(6)

        add_file_btn = QPushButton("Add Local")
        add_file_btn.setFixedSize(100, 24)
        add_file_btn.clicked.connect(self._add_local_file)
        add_file_btn.setObjectName("addLocalButton")
        button_layout.addWidget(add_file_btn)

        add_link_btn = QPushButton("Add YouTube")
        add_link_btn.setFixedSize(100, 24)
        add_link_btn.clicked.connect(self._add_youtube_link)
        add_link_btn.setObjectName("addYoutubeButton")
        button_layout.addWidget(add_link_btn)

        button_layout.addStretch()
        layout.addWidget(button_row)

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 20%."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(
            int(hex_color[j : j + 2], 16) for j in (0, 2, 4)  # noqa: E203
        )
        darkened = tuple(int(c * 0.8) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def _load_sounds(self) -> None:
        """Load sounds from the folder in alphabetical order."""
        if not os.path.exists(self.folder_path):
            # Show message if folder doesn't exist
            folder_icon = (ICON_DIR / 'folder.svg').as_posix()
            no_folder_label = QLabel(
                (
                    f"<img src='{folder_icon}' width='16' height='16'/> "
                    f"Folder '{self.folder_path}' not found"
                ),
            )
            no_folder_label.setTextFormat(Qt.RichText)
            no_folder_label.setAlignment(Qt.AlignCenter)
            no_folder_label.setObjectName('noFolderLabel')
            self.players_layout.addWidget(no_folder_label)
            return

        # Supported audio formats
        audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}

        # Find all audio files and folders
        audio_files = []
        sound_folders = []

        for item_path in Path(self.folder_path).iterdir():
            if (
                item_path.is_file()
                and item_path.suffix.lower() in audio_extensions
            ):
                audio_files.append(str(item_path))
            elif item_path.is_dir() and "EFFECTS" in self.title:
                # Only add folders for effects section
                # Check if folder contains any audio files
                has_audio = any(
                    f.is_file() and f.suffix.lower() in audio_extensions
                    for f in item_path.iterdir()
                )
                if has_audio:
                    sound_folders.append(str(item_path))

        # Sort files and folders alphabetically by name (case-insensitive)
        audio_files.sort(key=lambda x: Path(x).stem.lower())
        sound_folders.sort(key=lambda x: Path(x).name.lower())

        # Combine folders first, then files (so folders appear at the top)
        all_items = sound_folders + audio_files

        # Load any YouTube links from csv
        youtube_links = []
        csv_path = Path(self.folder_path) / "youtube_links.csv"
        if csv_path.exists():
            with csv_path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    url = row.get("url")
                    if url:
                        title = url
                        try:
                            _, title = self._resolve_youtube(url)
                        except Exception:
                            pass
                        youtube_links.append((url, title))

        if not all_items and not youtube_links:
            # Show message if no audio files or folders found
            music_icon = (ICON_DIR / 'music.svg').as_posix()
            if 'EFFECTS' in self.title:
                message = (
                    f"<img src='{music_icon}' width='16' height='16'/> "
                    "No audio files or folders found"
                    "<br>Add audio files or folders with sounds!"
                )
            else:
                message = (
                    f"<img src='{music_icon}' width='16' height='16'/> "
                    "No audio files found"
                    "<br>Drop some music here!"
                )

            no_files_label = QLabel()
            no_files_label.setTextFormat(Qt.RichText)
            no_files_label.setText(message)
            no_files_label.setAlignment(Qt.AlignCenter)
            no_files_label.setObjectName('noFilesLabel')
            self.players_layout.addWidget(no_files_label)
            return

        # Create players for local items
        for i, item_path in enumerate(all_items):
            is_folder = os.path.isdir(item_path)
            player = SoundPlayer(
                item_path,
                self.loop_mode,
                is_folder=is_folder,
                service=self._service,
            )
            self.players.append(player)
            self.players_layout.addWidget(player)

            if i < len(all_items) - 1 or youtube_links:
                divider = QFrame()
                divider.setFrameShape(QFrame.HLine)
                divider.setFrameShadow(QFrame.Sunken)
                divider.setFixedHeight(1)
                divider.setObjectName("dividerFrame")
                self.players_layout.addWidget(divider)

        # Create players for YouTube links
        for j, (url, title) in enumerate(youtube_links):
            player = SoundPlayer(
                url,
                self.loop_mode,
                service=self._service,
                is_stream=True,
                display_name=title,
            )
            self.players.append(player)
            self.players_layout.addWidget(player)

            if j < len(youtube_links) - 1:
                divider = QFrame()
                divider.setFrameShape(QFrame.HLine)
                divider.setFrameShadow(QFrame.Sunken)
                divider.setFixedHeight(1)
                divider.setObjectName("dividerFrame")
                self.players_layout.addWidget(divider)

        # Add stretch to push players to the top
        self.players_layout.addStretch()

    def _resolve_youtube(self, url: str) -> tuple[str, str]:
        """Wrapper for :func:`resolve_youtube` for backward compatibility."""
        return resolve_youtube(url)

    def _add_local_file(self) -> None:
        """Open a file dialog and copy selected file into section folder."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.m4a *.flac *.aac)",
        )
        if file_path:
            dest = Path(self.folder_path) / Path(file_path).name
            try:
                shutil.copy(file_path, dest)
            except Exception:
                return
            self.refresh()

    def _add_youtube_link(self) -> None:
        """Prompt for a YouTube link and store it in the local CSV."""
        link, ok = QInputDialog.getText(self, "Add YouTube Link", "URL:")
        if ok and link:
            csv_path = Path(self.folder_path) / "youtube_links.csv"
            new_file = not csv_path.exists()
            with csv_path.open("a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if new_file:
                    writer.writerow(["url"])
                writer.writerow([link])
            self.refresh()

    def stop_all(self) -> None:
        """Stop all players in this section."""
        for player in self.players:
            player.stop()

    def refresh(self) -> None:
        """Reload sounds from the section's folder."""
        # Stop any currently playing sounds
        self.stop_all()

        # Remove all existing player widgets and other layout items
        while self.players_layout.count():
            item = self.players_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Clear current players list and repopulate
        self.players = []
        self._load_sounds()
