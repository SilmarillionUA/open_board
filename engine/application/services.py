from PySide6.QtCore import QObject, Signal

from engine.application.repositories import SoundRepository
from engine.domain.sound import Sound


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

    def stop_sound(self, sound: Sound) -> None:
        """Stop playback and reset position for a sound."""

        self._repo.stop(sound)

    def set_master_volume(self, volume: float) -> None:
        """Adjust master output volume."""

        self._repo.set_master_volume(volume)
        self.master_volume_changed.emit(volume)

    def set_sound_volume(self, sound: Sound, volume: float) -> None:
        """Adjust volume for an individual sound."""

        self._repo.set_volume(sound, volume)

    def get_sound_position(self, sound: Sound) -> int:
        """Return current playback position for ``sound`` in ms."""

        return self._repo.get_position(sound)

    def set_sound_position(self, sound: Sound, position: int) -> None:
        """Seek ``sound`` to ``position`` (in ms)."""

        self._repo.set_position(sound, position)
