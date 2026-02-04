"""Script de prueba y verificar que funciones del proyecto funcionan correctamente."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_imports():
    """Prueba que todos los módulos se importan correctamente."""
    # Verificar importaciones básicas sin excepciones


def test_loader(tmp_path):
    """Prueba el cargador de audio con un archivo WAV temporal."""
    # Crear un pequeño WAV de prueba
    import numpy as np
    import soundfile as sf

    from audio import load_audio

    wav_path = tmp_path / "test.wav"
    data = 0.1 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
    sf.write(str(wav_path), data, 16000)

    result = load_audio(str(wav_path))
    assert os.path.exists(result)


def test_output_clipboard(monkeypatch):
    """Prueba guardado en portapapeles usando un mock."""
    copied = {}

    def fake_copy(text):
        copied["text"] = text

    monkeypatch.setattr("pyperclip.copy", fake_copy)

    from output import copy_to_clipboard

    texto_prueba = "Esto es una prueba de portapapeles"
    copy_to_clipboard(texto_prueba)
    assert copied.get("text") == texto_prueba


def test_output_file(tmp_path):
    """Prueba guardado en archivo."""
    from output import save_to_txt

    texto_prueba = """Esto es una prueba de archivo
        Con múltiples líneas
        """
    archivo_prueba = tmp_path / "test_output.txt"
    save_to_txt(texto_prueba, str(archivo_prueba))

    assert archivo_prueba.exists()
    contenido = archivo_prueba.read_text(encoding="utf-8")
    assert "Esto es una prueba de archivo" in contenido


def test_transcriber(monkeypatch, tmp_path):
    """Prueba de transcripción con un modelo mockeado."""
    import numpy as np

    # Crear archivo de audio temporal
    import soundfile as sf

    wav_path = tmp_path / "test_trans.wav"
    data = 0.1 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
    sf.write(str(wav_path), data, 16000)

    # Mockear whisper.load_model y su método transcribe
    class FakeModel:
        def transcribe(self, audio, language="es", verbose=False):
            return {"text": "hola mundo"}

    monkeypatch.setattr("whisper.load_model", lambda model: FakeModel())

    from transcription import transcribe_audio

    texto = transcribe_audio(str(wav_path))
    assert texto is not None
    assert "hola" in texto


def main():
    """Función principal para ejecutar todas las pruebas."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " PRUEBAS DEL PROYECTO DE AUTOMATIZACIÓN DE AUDIO ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")

    results = []

    # Ejecutar pruebas
    results.append(("Importaciones", test_imports()))
    results.append(("Cargador de Audio", test_loader()))
    results.append(("Portapapeles", test_output_clipboard()))
    results.append(("Archivo de Salida", test_output_file()))
    results.append(("Transcripción", test_transcriber()))

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)

    for nombre, resultado in results:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{nombre:<30} {estado}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} pruebas pasadas")

    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron")


if __name__ == "__main__":
    main()
