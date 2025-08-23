"""Repository interfaces for the application layer."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from PySide6.QtCore import QObject, Signal

from engine.domain.sound import Sound


# Create a metaclass that combines Qt's ``QObject`` metaclass with ``ABCMeta``.
#
# ``QObject`` classes use a special metaclass provided by PySide6. When
# combined with ``ABC`` (which uses ``ABCMeta``), Python raises a metaclass
# conflict. Subclassing both metaclasses resolves the issue and still allows the
# use of ``@abstractmethod``.


class _QObjectABCMeta(type(QObject), ABCMeta):
    """Metaclass combining PySide6's QObject meta and ``ABCMeta``."""


class SoundRepository(QObject, metaclass=_QObjectABCMeta):
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

    @abstractmethod
    def set_volume(self, sound: Sound, volume: float) -> None:
        """Set volume for a specific sound (0.0 to 1.0)."""
