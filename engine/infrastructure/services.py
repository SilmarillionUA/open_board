"""Concrete audio services wiring repositories for the GUI layer."""

from engine.application.services import AudioService
from .repositories import QtSoundRepository


class QtAudioService(AudioService):
    """Audio service backed by :class:`QtSoundRepository`."""

    def __init__(self) -> None:
        super().__init__(QtSoundRepository())
