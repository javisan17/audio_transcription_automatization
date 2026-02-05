"""Package to manage the output of transcripts."""

from .clipboard import copy_to_clipboard
from .text_file import save_to_txt


__all__ = ["copy_to_clipboard", "save_to_txt"]