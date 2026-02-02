"""Paquete encargado de la lógica de transcripción de voz a texto con Whisper."""

from .transcriber import transcribe_audio


__all__ = ["transcribe_audio"]