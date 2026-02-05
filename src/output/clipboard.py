# src/output/clipboard.py

"""Module for interaction with the system clipboard."""

import pyperclip


def copy_to_clipboard(text):
    """Copy the text to the clipboard."""
    pyperclip.copy(text)