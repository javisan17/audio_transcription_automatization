"""Paquete para gestionar la salida de las transcripciones."""

from .clipboard import copy_to_clipboard
from .text_file import save_to_txt


__all__ = ["copy_to_clipboard", "save_to_txt"]