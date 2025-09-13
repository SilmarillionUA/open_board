from pathlib import Path
from typing import Dict

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

from engine.application.repositories import SoundRepository
from engine.domain.sound import Sound


class QtSoundRepository(SoundRepository):
    """Sound repository backed by :class:`QMediaPlayer` objects."""

    def __init__(self) -> None:
        super().__init__()
        self._players: Dict[Sound, QMediaPlayer] = {}
        self._outputs: Dict[Sound, QAudioOutput] = {}
        self._volumes: Dict[Sound, float] = {}
        self._master_volume: float = 1.0

    def _ensure_player(self, sound: Sound) -> QMediaPlayer:
        player = self._players.get(sound)
        if player is None:
            player = QMediaPlayer()
            audio_output = QAudioOutput()
            player.setAudioOutput(audio_output)
            source: QUrl
            if isinstance(sound.path, Path) and sound.path.exists():
                source = QUrl.fromLocalFile(str(sound.path))
            else:
                source = QUrl.fromEncoded(str(sound.path).encode())
            player.setSource(source)
            self._players[sound] = player
            self._outputs[sound] = audio_output
            self._volumes.setdefault(sound, 1.0)
            # Emit playback finished when media ends and no looping
            player.mediaStatusChanged.connect(
                lambda status, s=sound: self._on_status_changed(s, status)
            )
        return player

    def _on_status_changed(
        self, sound: Sound, status: QMediaPlayer.MediaStatus
    ) -> None:
        if status == QMediaPlayer.EndOfMedia:
            if sound.should_loop():
                player = self._players.get(sound)
                if player:
                    player.setPosition(0)
                    player.play()
            else:
                self.playback_finished.emit(sound)

    def _apply_volume(self, sound: Sound) -> None:
        player = self._players.get(sound)
        output = self._outputs.get(sound)
        if player is None or output is None:
            return
        volume = self._volumes.get(sound, 1.0)
        output.setVolume(volume * self._master_volume)

    def play(self, sound: Sound) -> None:
        player = self._ensure_player(sound)
        self._apply_volume(sound)
        player.play()

    def pause(self, sound: Sound) -> None:
        player = self._players.get(sound)
        if player:
            player.pause()

    def stop(self, sound: Sound) -> None:
        player = self._players.get(sound)
        if player:
            player.stop()

    def set_master_volume(self, volume: float) -> None:
        self._master_volume = volume
        for snd in list(self._players.keys()):
            self._apply_volume(snd)

    def set_volume(self, sound: Sound, volume: float) -> None:
        self._volumes[sound] = volume
        self._apply_volume(sound)

    def get_position(self, sound: Sound) -> int:
        player = self._players.get(sound)
        if player:
            return player.position()
        return 0

    def set_position(self, sound: Sound, position: int) -> None:
        player = self._players.get(sound)
        if player:
            player.setPosition(position)
