# src/output/clipboard.py

"""Módulo para la interacción con el portapapeles del sistema."""

import pyperclip


def copy_to_clipboard(text):
    """Copia el texto al portapapeles."""
    pyperclip.copy(text)