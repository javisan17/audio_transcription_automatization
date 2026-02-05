""""Tests for the audio loader."""

import os

# Make sure src is in path
import sys

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from audio import loader


def test_load_nonexistent_raises():
    """Test that loading a non-existent file throws FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        loader.load_audio('nonexistent_file.wav')


def test_unsupported_extension(tmp_path):
    """Test that loading a file with an unsupported extension raises ValueError."""
    p = tmp_path / 'file.txt'
    p.write_text('not audio')
    with pytest.raises(ValueError):
        loader.load_audio(str(p))


def test_convert_mp4_to_wav_uses_ffmpeg(monkeypatch, tmp_path):
    """Test that the mp4 to wav conversion uses ffmpeg correctly."""
    # Create empty mp4 file
    mp4 = tmp_path / 'input.mp4'
    mp4.write_bytes(b'fake mp4 content')

    # Force get_ffmpeg_path to return something
    monkeypatch.setattr('audio.loader.get_ffmpeg_path', lambda: 'ffmpeg')

    # Mock subprocess.run to simulate success and create the WAV in the destination path
    class FakeResult:
        def __init__(self):
            self.returncode = 0
            self.stderr = ''

    def fake_run(cmd, capture_output=True, text=True, timeout=None):
        dest_wav = cmd[-1]
        # Create a simulated WAV file
        with open(dest_wav, 'wb') as f:
            f.write(b'RIFF....WAVE')
        return FakeResult()

    monkeypatch.setattr('audio.loader.subprocess.run', fake_run)

    out = loader.convert_mp4_to_wav(str(mp4))
    assert out.endswith('.wav')
    assert os.path.exists(out)
    os.remove(out)
