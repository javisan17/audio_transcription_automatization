"""Test script and verify which project functions work correctly."""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_imports():
    """Test that all modules are imported correctly."""
    # Check basic imports without exceptions


def test_loader(tmp_path):
    """Try the audio loader with a temporary WAV file."""
    # Create a small test WAV
    import numpy as np
    import soundfile as sf

    from audio import load_audio

    wav_path = tmp_path / "test.wav"
    data = 0.1 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
    sf.write(str(wav_path), data, 16000)

    result = load_audio(str(wav_path))
    assert os.path.exists(result)


def test_output_clipboard(monkeypatch):
    """Try saving to clipboard using a mock."""
    copied = {}

    def fake_copy(text):
        copied["text"] = text

    monkeypatch.setattr("pyperclip.copy", fake_copy)

    from output import copy_to_clipboard

    texto_prueba = "This is a clipboard test"
    copy_to_clipboard(texto_prueba)
    assert copied.get("text") == texto_prueba


def test_output_file(tmp_path):
    """Test saved in file."""
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
    """Transcription test with a mocked model."""
    import numpy as np

    # Create temporary audio file
    import soundfile as sf

    wav_path = tmp_path / "test_trans.wav"
    data = 0.1 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
    sf.write(str(wav_path), data, 16000)

    # Mock whisper.load_model and its transcribe method
    class FakeModel:
        def transcribe(self, audio, language="es", verbose=False):
            return {"text": "hola mundo"}

    monkeypatch.setattr("whisper.load_model", lambda model: FakeModel())

    from transcription import transcribe_audio

    texto = transcribe_audio(str(wav_path))
    assert texto is not None
    assert "hola" in texto


def main():
    """Run all tests."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " AUDIO AUTOMATION PROJECT TESTING ".center(58) + "║")
    logger.info("╚" + "=" * 58 + "╝")

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Audio Charger", test_loader()))
    results.append(("Clipboard", test_output_clipboard()))
    results.append(("Output File", test_output_file()))
    results.append(("Transcription", test_transcriber()))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY OF TESTS")
    logger.info("=" * 60)

    for nombre, resultado in results:
        estado = "✅ PASSED" if resultado else "❌ FAILED"
        logger.info(f"{nombre:<30} {estado}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED!")
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
