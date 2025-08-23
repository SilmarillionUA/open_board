from pathlib import Path
from typing import List

from engine.application.repositories import SoundRepository


class FileSystemSoundRepository(SoundRepository):
    """Loads audio paths from the local filesystem."""

    _AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"}

    def list_audio_files(self, folder_path: str) -> List[str]:
        base = Path(folder_path)
        if not base.exists():
            return []
        files = [
            str(p)
            for p in base.iterdir()
            if p.is_file() and p.suffix.lower() in self._AUDIO_EXTENSIONS
        ]
        return sorted(files, key=lambda x: Path(x).stem.lower())

    def list_audio_folders(self, folder_path: str) -> List[str]:
        base = Path(folder_path)
        if not base.exists():
            return []
        folders = []
        for p in base.iterdir():
            if p.is_dir():
                has_audio = any(
                    f.is_file() and f.suffix.lower() in self._AUDIO_EXTENSIONS
                    for f in p.iterdir()
                )
                if has_audio:
                    folders.append(str(p))
        return sorted(folders, key=lambda x: Path(x).name.lower())
