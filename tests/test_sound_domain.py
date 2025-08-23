import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine.domain.sound import Sound, SoundFolder, VolumeLevel


def test_volume_level_validation():
    VolumeLevel(0.5)
    with pytest.raises(ValueError):
        VolumeLevel(1.5)


def test_sound_folder_scan_filters_audio(tmp_path):
    (tmp_path / 'a.mp3').write_text('data')
    (tmp_path / 'b.txt').write_text('data')
    folder = SoundFolder(tmp_path)
    folder.scan()
    assert [s.path.name for s in folder.sounds] == ['a.mp3']


def test_sound_folder_random_sound(tmp_path):
    (tmp_path / 'a.mp3').write_text('data')
    (tmp_path / 'b.mp3').write_text('data')
    folder = SoundFolder(tmp_path)
    folder.scan()
    names = {folder.random_sound().path.name for _ in range(10)}
    assert names <= {'a.mp3', 'b.mp3'}
    assert names  # not empty


def test_sound_looping_flag(tmp_path):
    sound = Sound(tmp_path / 'a.mp3', loop=True)
    assert sound.should_loop()
    sound.loop = False
    assert not sound.should_loop()
