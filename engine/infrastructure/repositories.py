from __future__ import annotations

"""Concrete repository implementations using Qt multimedia classes."""

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

    # ------------------------------------------------------------------
    # Internal helpers
    def _ensure_player(self, sound: Sound) -> QMediaPlayer:
        player = self._players.get(sound)
        if player is None:
            player = QMediaPlayer()
            audio_output = QAudioOutput()
            player.setAudioOutput(audio_output)
            player.setSource(QUrl.fromLocalFile(str(sound.path)))
            self._players[sound] = player
            self._outputs[sound] = audio_output
            self._volumes.setdefault(sound, 1.0)
            # Emit playback finished when media ends and no looping
            player.mediaStatusChanged.connect(
                lambda status, s=sound: self._on_status_changed(s, status)
            )
        return player

    def _on_status_changed(self, sound: Sound, status: QMediaPlayer.MediaStatus) -> None:
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

    # ------------------------------------------------------------------
    # SoundRepository API
    def play(self, sound: Sound) -> None:  # pragma: no cover - Qt side effects
        player = self._ensure_player(sound)
        self._apply_volume(sound)
        player.play()

    def pause(self, sound: Sound) -> None:  # pragma: no cover - Qt side effects
        player = self._players.get(sound)
        if player:
            player.pause()

    def set_master_volume(self, volume: float) -> None:
        self._master_volume = volume
        for snd in list(self._players.keys()):
            self._apply_volume(snd)

    def set_volume(self, sound: Sound, volume: float) -> None:
        self._volumes[sound] = volume
        self._apply_volume(sound)
