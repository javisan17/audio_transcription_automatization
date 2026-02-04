"""Tests para el módulo transcription de audio."""

import os
import sys

import numpy as np


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from transcription import transcriber


def test_transcribe_alternative_path(monkeypatch, tmp_path):
    """Prueba que la transcripción usa el path alternativo si falla la primera vez."""
    # Crear archivo wav
    import soundfile as sf
    wav = tmp_path / 't.wav'
    data = 0.1 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
    sf.write(str(wav), data, 16000)

    # Mockear modelo que falla la primera vez
    class FakeModel:
        def transcribe(self, audio, language="es", verbose=False):
            if isinstance(audio, str):
                raise Exception('fallo al transcribir desde archivo')
            return {"text": "texto alternativo"}

    monkeypatch.setattr('whisper.load_model', lambda model: FakeModel())

    text = transcriber.transcribe_audio(str(wav))
    assert text is not None
    assert 'texto' in text
