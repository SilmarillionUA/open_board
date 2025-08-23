from typing import List, Protocol


class SoundRepository(Protocol):
    """Interface for accessing sound files from storage."""

    def list_audio_files(self, folder_path: str) -> List[str]:
        """Return a list of audio file paths inside the folder."""
        ...

    def list_audio_folders(self, folder_path: str) -> List[str]:
        """Return a list of subfolders containing audio files."""
        ...
