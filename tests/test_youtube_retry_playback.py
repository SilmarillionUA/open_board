import os
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine.application.repositories import SoundRepository
from engine.application.services import AudioService
from engine.infrastructure.widgets import SoundPlayer
from engine.domain.sound import Sound

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class DummyRepo(SoundRepository):
    def __init__(self) -> None:
        super().__init__()
        self.played = None

    def play(self, sound: Sound) -> None:  # pragma: no cover - dummy
        self.played = str(sound.path)

    def pause(self, sound: Sound) -> None:  # pragma: no cover - dummy
        pass

    def stop(self, sound: Sound) -> None:  # pragma: no cover - dummy
        pass

    def set_master_volume(self, volume: float) -> None:  # pragma: no cover - dummy
        pass

    def set_volume(self, sound: Sound, volume: float) -> None:  # pragma: no cover - dummy
        pass

    def get_position(self, sound: Sound) -> int:  # pragma: no cover - dummy
        return 0

    def set_position(self, sound: Sound, position: int) -> None:  # pragma: no cover - dummy
        pass


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_unresolved_link_resolves_on_play(monkeypatch):
    _ensure_app()
    repo = DummyRepo()
    service = AudioService(repo)

    monkeypatch.setattr(
        'engine.infrastructure.widgets.resolve_youtube',
        lambda url: ('http://stream', 'title'),
    )

    player = SoundPlayer(
        'https://youtube.com/watch?v=dummy',
        service=service,
        is_stream=True,
        stream_resolved=False,
    )

    player._start_playback()
    assert repo.played == 'http://stream'
