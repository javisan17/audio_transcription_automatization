"""Package responsible for speech-to-text transcription logic with Whisper."""

from .transcriber import transcribe_audio


__all__ = ["transcribe_audio"]