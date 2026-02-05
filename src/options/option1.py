# src/options/option1.py

"""Module for managing option 1 (file transcription)."""

import os

from audio import load_audio
from logger import get_logger
from output import copy_to_clipboard, save_to_txt
from transcription import transcribe_audio


logger = get_logger(__name__)


def option_1_transcribe_file():
    """Transcribes an existing audio file."""
    logger.info("\n=== OPTION 1: Transcribe File ===")
    file_path = input("Enter the path to the audio file: ").strip()

    if not os.path.isfile(file_path):
        logger.warning("The file does not exist.")
        return

    # Load and prepare audio
    prepared_audio = load_audio(file_path)

    # Transcribe
    text = transcribe_audio(prepared_audio)
    if not text:
        logger.error("Error during transcription.")
        return

    # Display text
    logger.info(f"\nTranscribed text:\n{text}\n")

    # Ask where to save
    output_option = input(
        "Where do you want to save? (1=Clipboard, 2=.txt file): "
    ).strip()

    if output_option == "1":
        copy_to_clipboard(text)
        logger.info("Text copied to clipboard.")

    elif output_option == "2":
        file_name = input(
            "File name (default: transcription.txt): "
        ).strip()
        file_name = file_name or "transcription.txt"
        save_to_txt(text, file_name)
        logger.info(f"Text saved in {file_name}")
        
    else:
        logger.warning("Invalid option.")