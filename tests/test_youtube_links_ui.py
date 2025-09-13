import os
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine.application.repositories import SoundRepository
from engine.application.services import AudioService
from engine.domain.sound import Sound
from engine.infrastructure.widgets import SoundSection

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class DummyRepo(SoundRepository):
    def __init__(self) -> None:
        super().__init__()

    def play(self, sound: Sound) -> None:  # pragma: no cover - dummy
        pass

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


def test_youtube_links_display_when_resolution_fails(tmp_path, monkeypatch):
    _ensure_app()

    (tmp_path / "youtube_links.csv").write_text(
        "url\nhttps://invalid.link\n", encoding="utf-8"
    )

    service = AudioService(DummyRepo())

    monkeypatch.setattr(
        SoundSection,
        "_resolve_youtube",
        lambda self, url: (_ for _ in ()).throw(Exception("fail")),
    )

    section = SoundSection("MUSIC", str(tmp_path), service)

    assert len(section.players) == 1
    assert section.players[0].file_path == "https://invalid.link"

