import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"}


@dataclass(frozen=True)
class VolumeLevel:
    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("Volume level must be between 0.0 and 1.0")


@dataclass(eq=False)
class Sound:
    path: Union[Path, str]
    loop: bool = False

    def should_loop(self) -> bool:
        return self.loop

    def __hash__(self) -> int:
        return hash(str(self.path))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Sound):
            return NotImplemented
        return str(self.path) == str(other.path)


@dataclass
class SoundFolder:
    path: Path
    sounds: List[Sound] = field(default_factory=list)

    def scan(self) -> None:
        if not self.path.exists() or not self.path.is_dir():
            self.sounds = []
            return
        self.sounds = [
            Sound(p)
            for p in self.path.iterdir()
            if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
        ]

    def random_sound(self) -> Optional[Sound]:
        if not self.sounds:
            return None
        return random.choice(self.sounds)
