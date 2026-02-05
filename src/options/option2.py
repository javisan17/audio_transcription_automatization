# src/options/option2.py

"""Module for the management of option 2 (real-time transcription)."""

from audio import record_audio
from logger import get_logger
from output import copy_to_clipboard, save_to_txt
from transcription import transcribe_audio


logger = get_logger(__name__)


def option_2_record_and_transcribe():
    """Record audio in real time and transcribes it."""
    logger.info("\n=== OPTION 2: Record and Transcribe ===")

    # Ask for duration
    try:
        duration = int(
            input("How many seconds do you want to record? (dft: 30): ").strip() or "30"
        )

    except ValueError:
        logger.warning("You must enter a valid number.")
        return

    # Record
    recorded_audio = record_audio(duration=duration)
    if not recorded_audio:
        logger.error("Error during recording.")
        return

    # Transcribe
    text = transcribe_audio(recorded_audio)
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