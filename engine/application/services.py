"""Application services coordinating sound playback."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from engine.domain.sound import Sound
from .repositories import SoundRepository


class AudioService(QObject):
    """High level service for controlling audio playback."""

    playback_finished = Signal(Sound)
    master_volume_changed = Signal(float)

    def __init__(self, repository: SoundRepository) -> None:
        super().__init__()
        self._repo = repository
        # Forward repository events to consumers of this service
        self._repo.playback_finished.connect(self.playback_finished)

    def play_sound(self, sound: Sound) -> None:
        """Play a sound through the repository."""
        self._repo.play(sound)

    def pause_sound(self, sound: Sound) -> None:
        """Pause a playing sound."""
        self._repo.pause(sound)

    def set_master_volume(self, volume: float) -> None:
        """Adjust master output volume."""
        self._repo.set_master_volume(volume)
        self.master_volume_changed.emit(volume)
