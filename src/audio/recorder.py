# src/audio/recorder.py

"""Real-time audio recording management."""
import tempfile
import threading

import numpy as np
import sounddevice as sd
import soundfile as sf

from logger import get_logger


logger = get_logger(__name__)


class AudioRecorder:
    """Audio recorder with start/stop control."""

    def __init__(self):
        """Initialize the status of the recorder and the audio buffer."""
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 16000
        self.thread = None

    def start_recording(self):
        """Start audio recording."""
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_data = []

        import logging
        logger = logging.getLogger(__name__)
        logger.info("Starting recording... (press STOP in the GUI to stop)")

        # Start recording in a separate thread
        self.thread = threading.Thread(target=self._record_stream, daemon=True)
        self.thread.start()

    def _record_stream(self):
        """Continuous recording stream."""
        try:
            # Check devices
            devices = sd.query_devices()
            input_devices = [
                i for i, dev in enumerate(devices) if dev["max_input_channels"] > 0
            ]

            if not input_devices:
                logger.warning("No input audio devices found.")
                self.is_recording = False
                return

            device = None  # Default

            #Use stream for continuous recording
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.debug(f"Stream status: {status}")
                # Copy audio data
                self.audio_data.append(indata.copy())

            # Create audio stream
            with sd.InputStream(
                callback=audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=4096,
                device=device,
            ):
                # Record while is_recording is True
                while self.is_recording:
                    sd.sleep(100)  # Small pause to not consume CPU

        except Exception as e:
            logger.exception(f"Error during recording: {e}")
            self.is_recording = False

    def stop_recording(self) -> str:
        """Stop recording and returns the WAV file path."""
        if not self.is_recording:
            return None

        self.is_recording = False

        # Wait for the thread to end
        if self.thread:
            self.thread.join(timeout=2)

        logger.info("Recording stopped")

        if not self.audio_data:
            logger.warning("No audio was recorded")
            return None

        # Concatenate all audio blocks
        audio_array = np.concatenate(self.audio_data, axis=0)

        # Convert to float32
        audio_array = audio_array.astype(np.float32)

        # Normalize if necessary
        max_val = np.abs(audio_array).max()
        if max_val > 1.0:
            audio_array = audio_array / max_val

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_wav = temp_file.name
        sf.write(temp_wav, audio_array, self.sample_rate)

        logger.info(f"Saved Audio: {temp_wav}")
        return temp_wav


# Global recorder instance
global_recorder = AudioRecorder()


def start_recording() -> None:
    """Start audio recording."""
    global_recorder.start_recording()


def stop_recording() -> str:
    """Stop recording and returns the WAV file path."""
    return global_recorder.stop_recording()


def record_audio(duration: int = 30, sample_rate: int = 16000) -> str:
    """Legacy function for compatibility.

    Record audio for a specific time.
    """
    logger.info(f"Recording for {duration} seconds...")

    try:
        # Check available devices
        devices = sd.query_devices()
        input_devices = [
            i for i, dev in enumerate(devices) if dev["max_input_channels"] > 0
        ]

        if not input_devices:
            raise RuntimeError("No audio input devices found.")

        #Use the default device or the first available
        device = None # Default

        # Record audio
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32,
            device=device,
        )

        # Wait for the recording to finish
        sd.wait()

        # Verify that something was recorded
        if np.abs(audio_data).max() < 0.01:
            raise RuntimeError("No audio detected. Verify the microphone is working.")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_wav = temp_file.name
        sf.write(temp_wav, audio_data, sample_rate)

        logger.info(f"Recording completed: {temp_wav}")
        return temp_wav

    except KeyboardInterrupt:
        logger.info("\nRecording cancelled.")
        return None

    except Exception as e:
        logger.error(f"Error during recording: {e}")
        return None
