"""Repository interfaces for the application layer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from PySide6.QtCore import QObject, Signal

from engine.domain.sound import Sound


class SoundRepository(QObject, ABC):
    """Abstract repository controlling sound playback.

    Infrastructure implementations should handle the actual audio I/O.
    """

    playback_finished = Signal(Sound)

    @abstractmethod
    def play(self, sound: Sound) -> None:
        """Play the given sound."""

    @abstractmethod
    def pause(self, sound: Sound) -> None:
        """Pause playback for the given sound."""

    @abstractmethod
    def set_master_volume(self, volume: float) -> None:
        """Set the global master volume (0.0 to 1.0)."""
