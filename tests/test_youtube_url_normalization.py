import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from engine.infrastructure.widgets import resolve_youtube  # noqa: E402


def test_music_youtube_url_normalized(monkeypatch):
    def fake_youtube(url):
        raise RuntimeError(url)

    monkeypatch.setattr("pytube.YouTube", fake_youtube)

    with pytest.raises(RuntimeError) as exc:
        resolve_youtube("https://music.youtube.com/watch?v=dummy")

    assert exc.value.args[0].startswith(
        "https://www.youtube.com/watch?v=dummy"
    )


def test_youtu_be_url_normalized(monkeypatch):
    def fake_youtube(url):
        raise RuntimeError(url)

    monkeypatch.setattr("pytube.YouTube", fake_youtube)

    with pytest.raises(RuntimeError) as exc:
        resolve_youtube("https://youtu.be/dummy")

    assert exc.value.args[0].startswith(
        "https://www.youtube.com/watch?v=dummy"
    )
