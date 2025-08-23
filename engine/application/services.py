from typing import Protocol
from PySide6.QtCore import Signal


class AudioService(Protocol):
    """Interface for audio playback operations."""

    playback_state_changed: Signal

    def play(self, path: str, loop: bool = False) -> None:
        """Play an audio file."""
        ...

    def pause(self, path: str) -> None:
        """Pause the audio file."""
        ...

    def stop(self, path: str) -> None:
        """Stop the audio file."""
        ...

    def set_volume(self, path: str, volume: float) -> None:
        """Set volume for the given audio file (0.0 - 1.0)."""
        ...

    def set_master_volume(self, volume: float) -> None:
        """Set master volume affecting all players."""
        ...

    def stop_all(self) -> None:
        """Stop all playing audio."""
        ...
