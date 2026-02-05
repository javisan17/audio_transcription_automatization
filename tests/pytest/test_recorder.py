"""Tests for the audio recorder."""

import os
import sys

import numpy as np


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from audio import recorder


def test_record_audio_no_devices(monkeypatch):
    """Test recording when no devices are available."""
    monkeypatch.setattr('audio.recorder.sd.query_devices', lambda: [])
    result = recorder.record_audio(duration=1)
    assert result is None


def test_record_audio_success(monkeypatch, tmp_path):
    """Test successful audio recording."""
    # Simulate available devices
    monkeypatch.setattr('audio.recorder.sd.query_devices',
                        lambda: [{'max_input_channels': 1}])

    # Mockear sd.rec y sd.wait
    def fake_rec(count, samplerate, channels, dtype, device):
        # Return an array with enough energy
        return np.ones((int(1 * samplerate), channels), dtype=np.float32) * 0.1

    monkeypatch.setattr('audio.recorder.sd.rec', fake_rec)
    monkeypatch.setattr('audio.recorder.sd.wait', lambda: None)

    path = recorder.record_audio(duration=1)
    assert path is not None
    assert os.path.exists(path)
    os.remove(path)


def test_audio_recorder_stop_creates_file(tmp_path):
    """Test that stop_recording creates a WAV file."""
    a = recorder.AudioRecorder()
    # Simulate that you were recording
    a.is_recording = True
    import numpy as np
    a.audio_data = [np.ones((10, 1),
                    dtype=np.float32) * 0.1,
                    np.ones((10, 1),
                    dtype=np.float32) * 0.1]

    wav = a.stop_recording()
    assert wav is not None
    assert os.path.exists(wav)
    os.remove(wav)
