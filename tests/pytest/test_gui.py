"""Tests for the audio transcription graphical user interface."""

import os
import sys
import tkinter as tk


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gui.gui_app import AudioTranscriptionGUI


def test_gui_transcribe_file(monkeypatch, tmp_path):
    """Test the transcription of a file from the GUI."""
    # Create wav file
    import numpy as np
    import soundfile as sf

    wav = tmp_path / 'g.wav'
    data = 0.1 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
    sf.write(str(wav), data, 16000)

    # Ensure that Tk is available, or skip the test
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        import pytest
        pytest.skip('Tk not available in this environment')

    # Mock load_audio and transcribe_audio in GUI module
    monkeypatch.setattr('gui.gui_app.load_audio', lambda p: str(wav))
    monkeypatch.setattr('gui.gui_app.transcribe_audio', lambda p: 'texto GUI')

    # Mock messagebox to avoid dialogs
    calls = {}
    monkeypatch.setattr('tkinter.messagebox.showinfo', 
                        lambda *a, **k: calls.setdefault('info', True))
    monkeypatch.setattr('tkinter.messagebox.showerror',
                        lambda *a, **k: calls.setdefault('error', True))

    gui = AudioTranscriptionGUI(root)

    gui.selected_file = str(wav)
    # Directly call the method that normally runs in a thread
    gui._transcribe_file_thread()

    content = gui.result_text.get(1.0, tk.END).strip()
    assert 'texto GUI' in content

    root.destroy()


def test_gui_save_and_copy(monkeypatch, tmp_path):
    """Try saving to file and copying to clipboard from the GUI."""
    # Mock filedialog and messagebox
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
        pytest.skip('Tk not available in this environment')
    gui = AudioTranscriptionGUI(root)

    # Put text in the widget
    gui.result_text.insert(tk.END, 'text to save')

    gui.save_to_file()

    out_file = tmp_path / 'out.txt'
    assert out_file.exists()
    assert 'text to save' in out_file.read_text(encoding='utf-8')

    # Copy to clipboard by mocking the IMPORTED function in the GUI module
    captured = {}
    monkeypatch.setattr('gui.gui_app.copy_to_clipboard',
                        lambda t: captured.setdefault('text', t))

    gui.copy_to_clipboard()
    assert captured.get('text') == 'text to save'

    root.destroy()
