import os
import random
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import (
    Qt,
    QUrl,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
    Property,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QScrollArea,
    QFrame,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtGui import QFont


class SoundPlayer(QWidget):
    """Individual sound player widget with play/stop and volume controls."""

    volume_changed = Signal(float)  # Signal for master volume changes

    def __init__(
        self,
        file_path: str,
        loop_mode: bool = False,
        is_folder: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.file_path = file_path
        self.loop_mode = loop_mode
        self.is_folder = is_folder
        self.master_volume = 1.0
        self._current_fade_volume = 1.0  # For fade animations

        if self.is_folder:
            # For folders, store the folder path and load available sounds
            self.folder_path = file_path
            self.filename = Path(file_path).name
            self.folder_sounds = self._load_folder_sounds()
            self.current_sound_path = None
        else:
            # For regular files
            self.filename = Path(file_path).stem

        # Audio components
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        # Set initial source if not a folder
        if not self.is_folder:
            self.media_player.setSource(QUrl.fromLocalFile(file_path))

        self.media_player.mediaStatusChanged.connect(
            self._on_media_status_changed
        )
        self.media_player.playbackStateChanged.connect(
            self._on_playback_state_changed
        )

        # Volume fade animation
        self.fade_animation = QPropertyAnimation(self, b"fadeVolume")
        self.fade_animation.setDuration(3000)  # 3 seconds
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self._setup_ui()
        self._update_volume()

    def _load_folder_sounds(self) -> List[str]:
        """Load all audio files from the folder."""
        if not os.path.exists(self.folder_path) or not os.path.isdir(
            self.folder_path
        ):
            return []

        audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}
        sounds = []

        for file_path in Path(self.folder_path).iterdir():
            if (
                file_path.is_file()
                and file_path.suffix.lower() in audio_extensions
            ):
                sounds.append(str(file_path))

        return sounds

    def _get_random_sound(self) -> Optional[str]:
        """Get a random sound from the folder."""
        if not self.folder_sounds:
            return None
        return random.choice(self.folder_sounds)

    @Property(float)
    def fadeVolume(self) -> float:
        return self._current_fade_volume

    @fadeVolume.setter  # type: ignore[no-redef]
    def fadeVolume(self, value: float) -> None:
        self._current_fade_volume = value
        self._update_volume()

    def _setup_ui(self) -> None:
        """Set up the player UI."""
        self.setMinimumHeight(80)
        self.setMaximumHeight(80)
        self.setStyleSheet(
            """
            SoundPlayer {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;  
                margin: 4px;  
            }
            SoundPlayer:hover {
                border-color: #2196F3;
            }
        """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(4)

        # Top row: Sound name with folder icon if applicable
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Sound name with folder indicator
        name_text = self.filename
        if self.is_folder:
            name_text = f"📁 {self.filename} 🔄"  # Folder icon + repeat icon

        self.name_label = QLabel(name_text)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 12px;  
                color: #333;
                padding: 2px 6px;
                background-color: transparent;
            }
        """
        )
        top_layout.addWidget(self.name_label, 1)

        main_layout.addLayout(top_layout)

        # Bottom row: Controls + Volume (in one line)
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(6)

        # Smaller buttons
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(28, 24)
        self.play_button.clicked.connect(self.play)
        self.play_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 12px;  
                font-weight: bold;
                font-size: 10px; 
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: #3d8b40;
            }
        """
        )
        bottom_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("⏸")
        self.pause_button.setFixedSize(28, 24)
        self.pause_button.clicked.connect(self._pause)
        self.pause_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #FF9800, stop:1 #F57C00);
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #F57C00, stop:1 #E65100);
            }
            QPushButton:pressed {
                background: #E65100;
            }
        """
        )
        self.pause_button.hide()
        bottom_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("⏹")
        self.stop_button.setFixedSize(28, 24)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f44336, stop:1 #da190b);
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #da190b, stop:1 #c1170a);
            }
            QPushButton:pressed {
                background: #c1170a;
            }
        """
        )
        bottom_layout.addWidget(self.stop_button)

        # Volume controls (inline)
        vol_label = QLabel("Vol:")
        vol_label.setStyleSheet(
            """
            QLabel {
                color: #666;
                font-size: 10px;   
                font-weight: bold;
            }
        """
        )
        bottom_layout.addWidget(vol_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedHeight(16)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        self.volume_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #ddd;
                height: 4px;  
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f5f5f5, stop:1 #e0e0e0);
                margin: 2px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2196F3, stop:1 #1976D2);
                border: 1px solid white;
                width: 12px;  
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1976D2, stop:1 #1565C0);
            }
        """
        )
        bottom_layout.addWidget(self.volume_slider, 1)

        self.volume_label = QLabel("70%")
        self.volume_label.setFixedWidth(30)
        self.volume_label.setStyleSheet(
            """
            QLabel {
                color: #666;
                font-size: 10px;
                font-weight: bold;
                text-align: right;
            }
        """
        )
        bottom_layout.addWidget(self.volume_label)

        main_layout.addLayout(bottom_layout)

        # Add folder info if this is a folder
        if self.is_folder:
            info_label = QLabel(f"({len(self.folder_sounds)} sounds)")
            info_label.setStyleSheet(
                """
                QLabel {
                    color: #888;
                    font-size: 9px;
                    font-style: italic;
                    padding: 0px 6px;
                }
            """
            )
            main_layout.addWidget(info_label)

    def _on_playback_state_changed(
        self, state: QMediaPlayer.PlaybackState
    ) -> None:
        """Handle playback state changes to show/hide buttons."""
        if state == QMediaPlayer.PlayingState:
            self.play_button.hide()
            self.pause_button.show()
        else:
            self.pause_button.hide()
            self.play_button.show()

    def play(self) -> None:
        """Start playing the sound with fade in for looping sounds only."""
        if self.is_folder:
            # For folders, select a random sound each time
            random_sound = self._get_random_sound()
            if random_sound:
                self.current_sound_path = random_sound
                self.media_player.setSource(QUrl.fromLocalFile(random_sound))
                print(
                    f"Playing random sound from folder '{self.filename}': "
                    f"{Path(random_sound).stem}"
                )
            else:
                print(f"No sounds found in folder '{self.filename}'")
                return

        self.media_player.play()
        if (
            self.loop_mode
        ):  # Only fade for ambient/music (folders are always effects, so no fade)
            try:
                self.fade_animation.finished.disconnect()
            except:
                pass
            self.fade_animation.setStartValue(0.0)
            self.fade_animation.setEndValue(1.0)
            self.fade_animation.start()
        else:  # Effects (including folders) play immediately at full volume
            self._current_fade_volume = 1.0
            self._update_volume()

    def _pause(self) -> None:
        """Pause playing the sound with fade out for looping sounds only."""
        if not self.loop_mode:  # Only fade for ambient/music
            self.media_player.pause()
            return 

        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
        self.fade_animation.finished.connect(
            lambda: self.media_player.pause()
        )
        self.fade_animation.setStartValue(self._current_fade_volume)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()

    def stop(self) -> None:
        """Stop playing the sound with fade out for looping sounds only."""
        if self.media_player.playbackState() != QMediaPlayer.StoppedState:
            if self.loop_mode:  # Only fade for ambient/music
                try:
                    self.fade_animation.finished.disconnect()
                except:
                    pass
                self.fade_animation.finished.connect(self._complete_stop)
                self.fade_animation.setStartValue(self._current_fade_volume)
                self.fade_animation.setEndValue(0.0)
                self.fade_animation.start()
            else:  # Effects (including folders) stop immediately
                self._complete_stop()
        else:
            self._complete_stop()

    def _on_volume_changed(self, value: int) -> None:
        """Handle volume slider changes."""
        self.volume_label.setText(f"{value}%")
        self._update_volume()

    def _update_volume(self) -> None:
        """Update the actual audio volume based on slider, master, and fade volume."""
        slider_volume = self.volume_slider.value() / 100.0
        final_volume = (
            slider_volume * self.master_volume * self._current_fade_volume
        )
        self.audio_output.setVolume(final_volume)

    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)."""
        self.master_volume = volume
        self._update_volume()

    def _on_media_status_changed(
        self, status: QMediaPlayer.MediaStatus
    ) -> None:
        """Handle media status changes for looping."""
        if status == QMediaPlayer.EndOfMedia and self.loop_mode:
            # Restart the media for looping
            self.media_player.setPosition(0)
            self.media_player.play()
        elif (
            status == QMediaPlayer.EndOfMedia
            and self.is_folder
            and not self.loop_mode
        ):
            # For folders, when a sound ends, we just stop (no auto-repeat)
            # User can click play again to get another random sound
            pass

    def _complete_stop(self) -> None:
        """Complete the stop action after fade."""
        self.media_player.stop()
        self._current_fade_volume = 1.0  # Reset for next play


class SoundSection(QWidget):
    """A section containing multiple sound players."""

    def __init__(
        self,
        title: str,
        folder_path: str,
        loop_mode: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.title = title
        self.folder_path = folder_path
        self.loop_mode = loop_mode
        self.players: List[SoundPlayer] = []

        self._setup_ui()
        self._load_sounds()

    def _setup_ui(self) -> None:
        """Set up the section UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Section header
        header = QLabel(self.title)
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(60)

        # Dynamic header colors based on section type
        if "AMBIENT" in self.title:
            header_color = "#4CAF50"
        elif "MUSIC" in self.title:
            header_color = "#2196F3"
        else:  # EFFECTS
            header_color = "#FF9800"

        header.setStyleSheet(
            f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {header_color}, stop:1 {self._darken_color(header_color)});
                color: white;
                border-radius: 12px 12px 0 0;
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
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: #fafafa;
                border-radius: 0 0 12px 12px;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """
        )

        self.players_widget = QWidget()
        self.players_widget.setStyleSheet("background-color: #fafafa;")
        self.players_layout = QVBoxLayout(self.players_widget)
        self.players_layout.setContentsMargins(8, 8, 8, 8)
        self.players_layout.setSpacing(6)

        scroll_area.setWidget(self.players_widget)
        layout.addWidget(scroll_area)

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 20%."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * 0.8) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def _load_sounds(self) -> None:
        """Load sound files and folders from the folder in alphabetical order."""
        if not os.path.exists(self.folder_path):
            # Show message if folder doesn't exist
            no_folder_label = QLabel(
                f"📁 Folder '{self.folder_path}' not found"
            )
            no_folder_label.setAlignment(Qt.AlignCenter)
            no_folder_label.setStyleSheet(
                """
                QLabel {
                    color: #999;
                    font-style: italic;
                    font-size: 14px;
                    padding: 40px 20px;
                    background-color: transparent;
                }
            """
            )
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

        if not all_items:
            # Show message if no audio files or folders found
            if "EFFECTS" in self.title:
                message = "🎵 No audio files or folders found\nAdd audio files or folders with sounds!"
            else:
                message = "🎵 No audio files found\nDrop some music here!"

            no_files_label = QLabel(message)
            no_files_label.setAlignment(Qt.AlignCenter)
            no_files_label.setStyleSheet(
                """
                QLabel {
                    color: #999;
                    font-style: italic;
                    font-size: 14px;
                    padding: 40px 20px;
                    background-color: transparent;
                    line-height: 1.5;
                }
            """
            )
            self.players_layout.addWidget(no_files_label)
            return

        # Create players for each item in alphabetical order
        for i, item_path in enumerate(all_items):
            is_folder = os.path.isdir(item_path)
            player = SoundPlayer(
                item_path, self.loop_mode, is_folder=is_folder
            )
            self.players.append(player)
            self.players_layout.addWidget(player)

            # Add divider after each player except the last one
            if i < len(all_items) - 1:
                divider = QFrame()
                divider.setFrameShape(QFrame.HLine)
                divider.setFrameShadow(QFrame.Sunken)
                divider.setFixedHeight(1)
                divider.setStyleSheet(
                    """
                    QFrame {
                        color: #e0e0e0;
                        background-color: #e0e0e0;
                        border: none;
                        margin: 2px 8px;
                    }
                """
                )
                self.players_layout.addWidget(divider)

        # Add stretch to push players to the top
        self.players_layout.addStretch()

    def set_master_volume(self, volume: float) -> None:
        """Set master volume for all players in this section."""
        for player in self.players:
            player.set_master_volume(volume)

    def stop_all(self) -> None:
        """Stop all players in this section."""
        for player in self.players:
            player.stop()
