# src/transcription/transcriber.py

"""Interface for the Whisper AI model and result processing."""

import threading

import numpy as np
import soundfile as sf
import whisper

from logger import get_logger


logger = get_logger(__name__)


def transcribe_audio(audio_path: str, model: str = "small") -> str | None:
    """Transcribe an audio file using Whisper.
    
    Supports wav, mp3, m4a, flac, ogg, mp4 files.
    Returns the transcribed text or None if there is an error.
    """
    result = [None]

    def transcribe_worker():
        try:
            logger.info(f"Cargando modelo Whisper ({model})...")
            whisper_model = whisper.load_model(model)

            logger.info(f"Transcribiendo audio: {audio_path}")

# Try to transcribe directly with Whisper (supports multiple formats)
            try:
                result[0] = whisper_model.transcribe(
                    audio_path, language="es", verbose=False
                )
                text = result[0].get("text", "").strip()
                if text:
                    logger.info("Transcription completed.")
                    result[0] = text
                else:
                    logger.warning("No text detected in the audio")
                    result[0] = "No audio content detected"

            except Exception as e:
                logger.warning(f"Attempt 1 failed: {e}")
                logger.info("Trying alternative method...")

                # If it fails, we try to load the audio directly with soundfile
                try:
                    audio_data, sr = sf.read(audio_path)

                    # Convert to float32
                    audio_data = audio_data.astype(np.float32)

                    # Convert to mono if stereo
                    if len(audio_data.shape) > 1:
                        audio_data = np.mean(audio_data, axis=1)

                    # Normalize if necessary
                    max_val = np.abs(audio_data).max()
                    if max_val > 1.0:
                        audio_data = audio_data / max_val

                    # Resample to 16kHz if necessary
                    if sr != 16000:
                        num_samples = int(len(audio_data) * 16000 / sr)
                        indices = np.linspace(0, len(audio_data) - 1, num_samples)
                        audio_data = np.interp(
                            indices, np.arange(len(audio_data)), audio_data
                        )

                    #Transcribe the audio in numpy format
                    result[0] = whisper_model.transcribe(
                        audio_data, language="es", verbose=False
                    )
                    text = result[0].get("text", "").strip()
                    if text:
                        logger.info("Transcription completed (alternative method).")
                        result[0] = text
                    else:
                        logger.warning("No text detected in the audio")
                        result[0] = "No audio content detected"

                except Exception as e2:
                    logger.error(f"Alternative method also failed:{e2}")
                    result[0] = None

        except Exception as e:
            logger.exception(f"Fatal error when transcribing: {e}")
            result[0] = None

    # Run with timeout
    thread = threading.Thread(target=transcribe_worker, daemon=True)
    thread.start()
    thread.join(timeout=300)  # 5 minutos timeout

    if thread.is_alive():
        logger.error("Transcription timeout exceeded (5 minutes)")
        return None

    return result[0]