""""Tests para el loader de audio."""

import os

# Asegurar que src esté en path
import sys

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from audio import loader


def test_load_nonexistent_raises():
    """Test que cargar un archivo inexistente lanza FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        loader.load_audio('nonexistent_file.wav')


def test_unsupported_extension(tmp_path):
    """Test que cargar un archivo con extensión no soportada lanza ValueError."""
    p = tmp_path / 'file.txt'
    p.write_text('not audio')
    with pytest.raises(ValueError):
        loader.load_audio(str(p))


def test_convert_mp4_to_wav_uses_ffmpeg(monkeypatch, tmp_path):
    """Test que la conversión de mp4 a wav usa ffmpeg correctamente."""
    # Crear archivo mp4 vacío
    mp4 = tmp_path / 'input.mp4'
    mp4.write_bytes(b'fake mp4 content')

    # Forzar que get_ffmpeg_path devuelva algo
    monkeypatch.setattr('audio.loader.get_ffmpeg_path', lambda: 'ffmpeg')

    # Mockear subprocess.run para simular éxito y crear el WAV en el path destino
    class FakeResult:
        def __init__(self):
            self.returncode = 0
            self.stderr = ''

    def fake_run(cmd, capture_output=True, text=True, timeout=None):
        dest_wav = cmd[-1]
        # Crear un archivo WAV simulado
        with open(dest_wav, 'wb') as f:
            f.write(b'RIFF....WAVE')
        return FakeResult()

    monkeypatch.setattr('audio.loader.subprocess.run', fake_run)

    out = loader.convert_mp4_to_wav(str(mp4))
    assert out.endswith('.wav')
    assert os.path.exists(out)
    os.remove(out)
