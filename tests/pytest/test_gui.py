"""Tests para la interfaz gráfica de usuario de transcripción de audio."""

import os
import sys
import tkinter as tk


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gui.gui_app import AudioTranscriptionGUI


def test_gui_transcribe_file(monkeypatch, tmp_path):
    """Testear la transcripción de un archivo desde la GUI."""
    # Crear archivo wav
    import numpy as np
    import soundfile as sf

    wav = tmp_path / 'g.wav'
    data = 0.1 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
    sf.write(str(wav), data, 16000)

    # Asegurar que Tk está disponible, o saltar la prueba
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        import pytest
        pytest.skip('Tk no disponible en este entorno')

    # Mockear load_audio y transcribe_audio en el módulo de la GUI
    monkeypatch.setattr('gui.gui_app.load_audio', lambda p: str(wav))
    monkeypatch.setattr('gui.gui_app.transcribe_audio', lambda p: 'texto GUI')

    # Mockear messagebox para evitar diálogos
    calls = {}
    monkeypatch.setattr('tkinter.messagebox.showinfo', 
                        lambda *a, **k: calls.setdefault('info', True))
    monkeypatch.setattr('tkinter.messagebox.showerror',
                        lambda *a, **k: calls.setdefault('error', True))

    gui = AudioTranscriptionGUI(root)

    gui.selected_file = str(wav)
    # Llamar directamente al método que normalmente corre en hilo
    gui._transcribe_file_thread()

    content = gui.result_text.get(1.0, tk.END).strip()
    assert 'texto GUI' in content

    root.destroy()


def test_gui_save_and_copy(monkeypatch, tmp_path):
    """Testear guardar en archivo y copiar al portapapeles desde la GUI."""
    # Mockear filedialog y messagebox
    monkeypatch.setattr('tkinter.filedialog.asksaveasfilename',
                        lambda **k: str(tmp_path / 'out.txt'))
    saved = {}
    monkeypatch.setattr('tkinter.messagebox.showinfo',
                        lambda *a, **k: saved.setdefault('info', True))

    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        import pytest
        pytest.skip('Tk no disponible en este entorno')
    gui = AudioTranscriptionGUI(root)

    # Poner texto en el widget
    gui.result_text.insert(tk.END, 'texto para guardar')

    gui.save_to_file()

    out_file = tmp_path / 'out.txt'
    assert out_file.exists()
    assert 'texto para guardar' in out_file.read_text(encoding='utf-8')

    # Copiar al portapapeles mockeando la función IMPORTADA en el módulo de la GUI
    captured = {}
    monkeypatch.setattr('gui.gui_app.copy_to_clipboard',
                        lambda t: captured.setdefault('text', t))

    gui.copy_to_clipboard()
    assert captured.get('text') == 'texto para guardar'

    root.destroy()
