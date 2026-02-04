"""Tests para las opciones de transcripción de audio."""

import builtins
import importlib.util
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Cargar módulos de opciones directamente desde archivos
def load_module_from_path(name, path):
    """Cargar un módulo desde una ruta específica."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

HERE = os.path.join(os.path.dirname(__file__), '..', 'src', 'options')
option1 = load_module_from_path('option1', os.path.join(HERE, 'option1.py'))
option2 = load_module_from_path('option2', os.path.join(HERE, 'option2.py'))


def test_option_1_copy_to_clipboard(monkeypatch, tmp_path):
    """Prueba opción 1: transcribir archivo y copiar al portapapeles."""
    # Preparar inputs: ruta del archivo, opción 1 (portapapeles)
    responses = iter([str(tmp_path / 'audio.wav'), '1'])
    monkeypatch.setattr(builtins, 'input', lambda *args: next(responses))

    # Mockear funciones usadas DENTRO del módulo cargado (referencias están allí)
    monkeypatch.setattr(option1, 'load_audio', lambda p: p)
    monkeypatch.setattr(option1, 'transcribe_audio', lambda p: 'texto prueba')

    called = {}

    def fake_copy(text):
        called['text'] = text

    monkeypatch.setattr(option1, 'copy_to_clipboard', fake_copy)

    # Crear archivo de audio simulado
    p = tmp_path / 'audio.wav'
    p.write_bytes(b'RIFF')

    option1.opcion_1_transcribir_archivo()
    assert called.get('text') == 'texto prueba'


def test_option_2_record_and_copy(monkeypatch, tmp_path):
    """Prueba opción 2: grabar audio y copiar transcripción al portapapeles."""
    # Inputs: duration, option to copy
    responses = iter(['1', '1'])
    monkeypatch.setattr(builtins, 'input', lambda *args: next(responses))

    # Mockear record_audio y transcribe DENTRO del módulo cargado
    monkeypatch.setattr(option2, 'record_audio',
                        lambda duration=30: str(tmp_path / 'rec.wav'))
    monkeypatch.setattr(option2, 'transcribe_audio',
                        lambda p: 'texto desde grabacion')

    called = {}
    monkeypatch.setattr(option2, 'copy_to_clipboard',
                        lambda text: called.setdefault('text', text))

    option2.opcion_2_grabar_y_transcribir()
    assert 'texto desde grabacion' in called.get('text', '')
