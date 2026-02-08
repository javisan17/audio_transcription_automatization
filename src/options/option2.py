# src/options/option2.py

"""Module for the management of option 2 (real-time transcription)."""

import threading

from audio import record_audio, start_recording, stop_recording
from logger import get_logger
from output import copy_to_clipboard, save_to_txt
from transcription import transcribe_audio


logger = get_logger(__name__)


def _record_by_time(duration: int) -> str:
    """Record audio for a specific duration."""
    logger.info(f"Recording for {duration} seconds...")
    recorded_audio = record_audio(duration=duration)
    return recorded_audio


def _record_interactive() -> str:
    """Record audio with start/stop control via terminal input."""
    logger.info("\n--- INTERACTIVE RECORDING MODE ---")
    logger.info("Press ENTER or type 'stop' to stop recording")
    logger.info("Starting recording now...\n")
    
    start_recording()
    
    # Wait for user input in a thread to not block recording
    stop_event = threading.Event()
    
    def wait_for_stop():
        while not stop_event.is_set():
            user_input = input().strip().lower()
            if user_input in ("stop", "s", ""):
                stop_event.set()
                break
    
    input_thread = threading.Thread(target=wait_for_stop, daemon=True)
    input_thread.start()
    
    # Wait for stop event
    input_thread.join()
    
    recorded_audio = stop_recording()
    if recorded_audio:
        logger.info("Recording completed.")
    return recorded_audio


def option_2_record_and_transcribe():
    """Record audio in real time and transcribes it."""
    logger.info("\n=== OPTION 2: Record and Transcribe ===")

    # Ask for recording mode
    mode = input("\nRecording mode:\n  1 = By time (seconds)\n  2 = Start/Stop control\nChoose (1 or 2): ").strip()

    recorded_audio = None

    if mode == "1":
        # Record by time
        try:
            duration = int(
                input("How many seconds do you want to record? (dft: 30): ").strip() or "30"
            )
        except ValueError:
            logger.warning("You must enter a valid number.")
            return

        recorded_audio = _record_by_time(duration)

    elif mode == "2":
        # Interactive start/stop
        recorded_audio = _record_interactive()

    else:
        logger.warning("Invalid mode selected.")
        return

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