import sys
from pathlib import Path
import urllib.error

sys.path.append(str(Path(__file__).resolve().parents[1]))
from engine.infrastructure.widgets import resolve_youtube  # noqa: E402


class _FakeStream:
    url = "stream"


class _FakeQuery:
    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def desc(self):
        return self

    def first(self):
        return _FakeStream()


class _FakeYT:
    def __init__(self, url):
        self.title = "title"
        self.streams = _FakeQuery()


def test_resolve_youtube_retries_on_error(monkeypatch):
    calls = []

    def fake_youtube(url):
        calls.append(url)
        if len(calls) < 3:
            raise urllib.error.HTTPError(
                url, 400, "Bad Request", None, None
            )
        return _FakeYT(url)

    monkeypatch.setattr("pytube.YouTube", fake_youtube)

    stream_url, title = resolve_youtube(
        "https://music.youtube.com/watch?v=dummy"
    )

    assert stream_url == "stream"
    assert title == "title"
    assert len(calls) == 3
