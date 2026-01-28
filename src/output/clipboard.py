# src/output/clipboard.py

import pyperclip


def copy_to_clipboard(text):
    """
    Copia el texto al portapapeles.
    """
    
    pyperclip.copy(text)