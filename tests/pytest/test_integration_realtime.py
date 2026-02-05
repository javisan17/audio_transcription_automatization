"""Integration test: real-time recording stream using generated audio.

This test runs `tests/audio/create_test_audio.py` in a temporary directory to
create `test_audio.wav`, then force the "Option 2" flow to use that file as
if it were audio recorded in real time. For security and so that it does not run in
each CI run, this test will SKIP by default unless the variable
environment `INTEGRATION_TESTS=1` is present.
"""

import builtins
import importlib.util
import os
import subprocess
import sys

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

HERE = os.path.dirname(__file__)


@pytest.mark.integration
@pytest.mark.skipif(os.environ.get('INTEGRATION_TESTS') != '1',
                    reason="Set INTEGRATION_TESTS=1 to run integration tests")
def test_integration_realtime_with_generated_audio(monkeypatch, tmp_path):
    """Test de integración del flujo de grabación en tiempo real con audio generado."""
    # Ejecutar el script que genera el audio de prueba en tmp_path
    script = os.path.join(HERE, 'audio', 'create_test_audio.py')
    # Ejecutar el script forzando UTF-8 en la salida para evitar errores de encoding
    env = os.environ.copy()
    env['PYTHONUTF8'] = '1'
    subprocess.run([sys.executable, script], cwd=str(tmp_path), check=True, env=env)

    audio_file = tmp_path / 'test_audio.wav'
    assert audio_file.exists(), "The script did not generate test_audio.wav"

    # Load the option2 module directly (avoid problems in the package's __init__)
    option2_path = os.path.join(os.path.dirname(__file__),
                                '..', 'src', 'options', 'option2.py')
    option2_path = os.path.abspath(option2_path)

    spec = importlib.util.spec_from_file_location('option2', option2_path)
    option2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(option2)

    # Force record_audio to return the generated file
    monkeypatch.setattr(option2, 'record_audio', lambda duration=30: str(audio_file))

    # Simulate inputs: duration (1) and output option (1 = clipboard)
    responses = iter(['1', '1'])
    monkeypatch.setattr(builtins, 'input', lambda *a, **k: next(responses))

    # Capture what would be copied to the clipboard
    captured = {}

    def fake_copy(text):
        captured['text'] = text

    monkeypatch.setattr(option2, 'copy_to_clipboard', fake_copy)

    # Run option 2 (do not mock transcription to make a more real test)
    option2.opcion_2_grabar_y_transcribir()

    # Verify that something was copied to the clipboard
    assert 'text' in captured, 'No text was copied to the clipboard'
    assert isinstance(captured['text'], str)
    assert len(captured['text']) > 0
