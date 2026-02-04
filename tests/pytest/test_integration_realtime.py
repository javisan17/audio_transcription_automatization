"""Prueba de integración: flujo de grabación en tiempo real usando un audio generado.

Esta prueba ejecuta `tests/audio/create_test_audio.py` en un directorio temporal para
crear `test_audio.wav`, luego fuerza al flujo de "Opción 2" a usar ese archivo como
si fuese audio grabado en tiempo real. Por seguridad y para que no se ejecute en
cada corrida de CI, esta prueba se SKIP por defecto a menos que la variable de
entorno `INTEGRATION_TESTS=1` esté presente.
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
    assert audio_file.exists(), "El script no generó test_audio.wav"

    # Cargar el módulo option2 directamente (evitar problemas en __init__ del paquete)
    option2_path = os.path.join(os.path.dirname(__file__),
                                '..', 'src', 'options', 'option2.py')
    option2_path = os.path.abspath(option2_path)

    spec = importlib.util.spec_from_file_location('option2', option2_path)
    option2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(option2)

    # Forzar que record_audio devuelva el archivo generado
    monkeypatch.setattr(option2, 'record_audio', lambda duration=30: str(audio_file))

    # Simular entradas: duración (1) y opción de salida (1 = portapapeles)
    responses = iter(['1', '1'])
    monkeypatch.setattr(builtins, 'input', lambda *a, **k: next(responses))

    # Capturar lo que se copiaría al portapapeles
    captured = {}

    def fake_copy(text):
        captured['text'] = text

    monkeypatch.setattr(option2, 'copy_to_clipboard', fake_copy)

    # Ejecutar la opción 2 (no mockear transcripción para hacer una prueba más real)
    option2.opcion_2_grabar_y_transcribir()

    # Verificar que se copió algo al portapapeles
    assert 'text' in captured, 'No se copió ningún texto al portapapeles'
    assert isinstance(captured['text'], str)
    assert len(captured['text']) > 0
