import os
from PySide6.QtWidgets import QApplication

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine.infrastructure.widgets import SoundSection


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_resolve_youtube_prefers_mp4(monkeypatch):
    _ensure_app()

    class DummyStream:
        def __init__(self, url, mime_type, abr):
            self.url = url
            self.mime_type = mime_type
            self.abr = abr

    class DummyQuery:
        def __init__(self, streams):
            self._streams = list(streams)

        def filter(self, only_audio=False, mime_type=None):
            filtered = [
                s
                for s in self._streams
                if (not only_audio or True)
                and (mime_type is None or s.mime_type == mime_type)
            ]
            return DummyQuery(filtered)

        def order_by(self, key):
            return DummyQuery(sorted(self._streams, key=lambda s: getattr(s, key)))

        def desc(self):
            return DummyQuery(list(reversed(self._streams)))

        def first(self):
            return self._streams[0] if self._streams else None

    class DummyYouTube:
        def __init__(self, url):
            self.streams = DummyQuery(
                [
                    DummyStream("webm_url", "audio/webm", 160),
                    DummyStream("mp4_url", "audio/mp4", 128),
                ]
            )
            self.title = "dummy"

    monkeypatch.setattr("pytube.YouTube", DummyYouTube)

    url, title = SoundSection._resolve_youtube(object(), "http://example.com")
    assert url == "mp4_url"
    assert title == "dummy"
