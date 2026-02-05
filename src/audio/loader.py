# src/audio/loader.py

"""Utilities for converting and validating audio formats."""

import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import suppress

from logger import get_logger


logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".mp4")


def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed and available in the PATH."""
    try:
        # On Windows look for ffmpeg.exe, on other systems ffmpeg
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return result.returncode == 0

    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_ffmpeg_path() -> str:
    """Get the full path of FFmpeg.

    On Windows, search common paths.
    """
    # First try to find ffmpeg in the PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    # On Windows, additional search on common paths
    if sys.platform.startswith("win"):
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            os.path.expanduser(r"~\ffmpeg\bin\ffmpeg.exe"),
        ]
        for path in common_paths:
            if os.path.isfile(path):
                return path

    return None


def convert_mp4_to_wav(mp4_path: str) -> str:
    """Convert an MP4 file to WAV using ffmpeg.

    Returns the path of the temporary WAV file.
    """
    temp_wav = None

    try:
        # Verify that the input file exists
        if not os.path.isfile(mp4_path):
            raise FileNotFoundError(f"El archivo MP4 no existe: {mp4_path}")

        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_wav = temp_file.name

        logger.info(f"Converting MP4 to WAV: {mp4_path}")
        logger.debug(f"Temporary file: {temp_wav}")

        # Check if FFmpeg is available
        ffmpeg_path = get_ffmpeg_path()

        if not ffmpeg_path:
            raise RuntimeError(
                "FFmpeg is not installed or is not found in the PATH.\n\n"
                "For Windows:\n"
                "1. Download FFmpeg from: https://ffmpeg.org/download.html#build-windows\n"
                "2. Extract the ZIP file\n"
                "3. Add the 'bin' folder to the system PATH\n"
                " Or copy ffmpeg.exe to: C:\\ffmpeg\\bin\\\n\n"
                "Then execute: uv sync"
            )

        # Prepare command with correct paths
        # On Windows, use quotes around paths that contain spaces
        cmd = [
            ffmpeg_path,
            "-i",
            mp4_path,
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-y",
            temp_wav,
        ]

        logger.debug(f"Running: {' '.join(cmd)}")

        # Run FFmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
        )

        if result.returncode != 0:
            # Clean temporary file if there is error
            if os.path.exists(temp_wav):
                with suppress(OSError):
                    os.remove(temp_wav)

            error_msg = result.stderr if result.stderr else "Unknown error"
            raise RuntimeError(
                f"FFmpeg error (code {result.returncode}): {error_msg}"
            )

        # Verify that the file was generated
        if not os.path.exists(temp_wav):
            raise RuntimeError("The WAV file was not generated (file not found)")

        file_size = os.path.getsize(temp_wav)
        if file_size == 0:
            raise RuntimeError("The WAV file is empty (0 bytes)")

        logger.info(f"Conversion completed: {temp_wav} ({file_size} bytes)")
        return temp_wav

    except Exception as e:
        # Clean temporary file in case of error
        if temp_wav and os.path.exists(temp_wav):
            with suppress(OSError):
                    os.remove(temp_wav)
        raise RuntimeError(f"Error converting MP4 to WAV: {str(e)}") from e


def load_audio(audio_path: str) -> str:
    """Validate an audio file.
    
    If it is MP4, it converts it to WAV automatically.
    Returns the absolute path to the audio.
    """
    # Convert to absolute path if relative
    audio_path = os.path.abspath(audio_path)

    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"No exists the file: {audio_path}")

    ext = os.path.splitext(audio_path)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Audio format not supported. Detected extension: {ext}")

    # If MP4, convert to WAV
    if ext == ".mp4":
        logger.info("MP4 file detected, converting to WAV...")
        return convert_mp4_to_wav(audio_path)

    return audio_path
