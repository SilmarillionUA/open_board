from engine.application.services import AudioService
from engine.infrastructure.repositories import QtSoundRepository


class QtAudioService(AudioService):
    """Audio service backed by :class:`QtSoundRepository`."""

    def __init__(self) -> None:
        super().__init__(QtSoundRepository())
