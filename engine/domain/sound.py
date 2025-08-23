from __future__ import annotations

"""Domain entity representing a sound clip."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Sound:
    """Represents an audio file that can be played.

    Attributes:
        path: Path to the audio file on disk.
        loop: Whether the sound should loop when played.
    """

    path: Path
    loop: bool = False
