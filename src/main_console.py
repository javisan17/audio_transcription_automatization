"""Main module for audio automation."""

from logger import get_logger, setup_logging
from options import option_1_transcribe_file, option_2_record_and_transcribe


setup_logging()
logger = get_logger(__name__)


def main():
    """Display the menu and handles user options."""
    logger.info("=" * 50)
    logger.info("AUDIO AUTOMATION -TRANSCRIPTION")
    logger.info("=" * 50)

    while True:
        logger.info("\nChoose an option:")
        logger.info("1 - Transcribe an audio file")
        logger.info("2 - Record audio and transcribe")
        logger.info("3 - Exit")

        opcion = input("\nOption (1/2/3): ").strip()

        if opcion == "1":
            option_1_transcribe_file()
        elif opcion == "2":
            option_2_record_and_transcribe()
        elif opcion == "3":
            logger.info("\nSee you later!")
            break
        else:
            logger.warning("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
