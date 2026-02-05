"""Tests for audio transcription options."""

import builtins
import importlib.util
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Load option modules directly from files
def load_module_from_path(name, path):
    """Load a module from a specific path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

HERE = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'options')
option1 = load_module_from_path('option1', os.path.join(HERE, 'option1.py'))
option2 = load_module_from_path('option2', os.path.join(HERE, 'option2.py'))


def test_option_1_copy_to_clipboard(monkeypatch, tmp_path):
    """Test option 1: transcribe file and copy to clipboard."""
    # Prepare inputs: file path, option 1 (clipboard)
    responses = iter([str(tmp_path / 'audio.wav'), '1'])
    monkeypatch.setattr(builtins, 'input', lambda *args: next(responses))

    # Mock functions used WITHIN the loaded module (references are there)
    monkeypatch.setattr(option1, 'load_audio', lambda p: p)
    monkeypatch.setattr(option1, 'transcribe_audio', lambda p: 'texto prueba')

    called = {}

    def fake_copy(text):
        called['text'] = text

    monkeypatch.setattr(option1, 'copy_to_clipboard', fake_copy)

    # Create simulated audio file
    p = tmp_path / 'audio.wav'
    p.write_bytes(b'RIFF')

    option1.option_1_transcribe_file()
    assert called.get('text') == 'texto prueba'


def test_option_2_record_and_copy(monkeypatch, tmp_path):
    """Test option 2: record audio and copy transcription to clipboard."""
    # Inputs: duration, option to copy
    responses = iter(['1', '1'])
    monkeypatch.setattr(builtins, 'input', lambda *args: next(responses))

    #Mock record_audio and transcribe INSIDE the loaded module
    monkeypatch.setattr(option2, 'record_audio',
                        lambda duration=30: str(tmp_path / 'rec.wav'))
    monkeypatch.setattr(option2, 'transcribe_audio',
                        lambda p: 'texto desde grabacion')

    called = {}
    monkeypatch.setattr(option2, 'copy_to_clipboard',
                        lambda text: called.setdefault('text', text))

    option2.option_2_record_and_transcribe()
    assert 'texto desde grabacion' in called.get('text', '')
