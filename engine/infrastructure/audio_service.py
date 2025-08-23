from __future__ import annotations

from typing import Callable, Dict

from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

from engine.application.services import AudioService


class QtAudioService(QObject, AudioService):
    """Qt-based implementation of the :class:`AudioService` interface."""

    playback_state_changed = Signal(str, bool)

    def __init__(self) -> None:
        super().__init__()
        self._players: Dict[str, QMediaPlayer] = {}
        self._outputs: Dict[str, QAudioOutput] = {}
        self._volumes: Dict[str, float] = {}
        self._looping: Dict[str, bool] = {}
        self._master_volume = 1.0

    # Internal helpers -------------------------------------------------
    def _get_player(self, path: str) -> QMediaPlayer:
        player = self._players.get(path)
        if player is None:
            player = QMediaPlayer()
            output = QAudioOutput()
            player.setAudioOutput(output)
            player.setSource(QUrl.fromLocalFile(path))
            player.playbackStateChanged.connect(
                lambda state, p=path: self.playback_state_changed.emit(
                    p, state == QMediaPlayer.PlayingState
                )
            )
            player.mediaStatusChanged.connect(
                lambda status, p=path: self._handle_status(p, status)
            )
            self._players[path] = player
            self._outputs[path] = output
        return player

    def _handle_status(
        self, path: str, status: QMediaPlayer.MediaStatus
    ) -> None:
        if status == QMediaPlayer.EndOfMedia and self._looping.get(path):
            player = self._players.get(path)
            if player:
                player.setPosition(0)
                player.play()

    def _apply_volume(self, path: str) -> None:
        output = self._outputs.get(path)
        if output:
            vol = self._volumes.get(path, 1.0)
            output.setVolume(vol * self._master_volume)

    # AudioService implementation -------------------------------------
    def play(self, path: str, loop: bool = False) -> None:
        player = self._get_player(path)
        self._looping[path] = loop
        self._apply_volume(path)
        player.play()

    def pause(self, path: str) -> None:
        player = self._players.get(path)
        if player:
            player.pause()

    def stop(self, path: str) -> None:
        player = self._players.get(path)
        if player:
            player.stop()
            player.setPosition(0)

    def set_volume(self, path: str, volume: float) -> None:
        self._volumes[path] = volume
        self._apply_volume(path)

    def set_master_volume(self, volume: float) -> None:
        self._master_volume = volume
        for path in list(self._players.keys()):
            self._apply_volume(path)

    def stop_all(self) -> None:
        for path in list(self._players.keys()):
            self.stop(path)
