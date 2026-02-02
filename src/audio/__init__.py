"""Lógica central para la captura y carga de señales de audio."""

from .loader import load_audio
from .recorder import record_audio


__all__ = ["load_audio", "record_audio"]
