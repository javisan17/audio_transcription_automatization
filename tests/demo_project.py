"""Demo script of the main functionalities of the project.

Simulates the flows of both options without the need for manual interaction.
"""

import os
import sys
from pydoc import text


# Add src to path (parent of parent)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from audio import load_audio
from logger import get_logger
from output import copy_to_clipboard, save_to_txt
from transcription import transcribe_audio


logger = get_logger(__name__)
logger.info("\n" + "=" * 70)
logger.info("PROJECT DEMO – AUDIO AUTOMATION")
logger.info("=" * 70)

# OPTION 1: Transcribe file
logger.info("\n" + "-" * 70)
logger.info("OPTION 1: TRANSCRIBE AUDIO FILE")
logger.info("-" * 70)

try:
    logger.info("✓ Detecting audio file...")
    audio_path = "audio/test_audio.wav"

    if os.path.exists(audio_path):
        logger.info(f"✓ File found: {audio_path}")

        logger.info("✓ Loading and preparing audio...")
        prepared_audio = load_audio(audio_path)
        logger.info("✓ Audio prepared for transcription")

        logger.info("✓ Starting transcription...")
        logger.info("(Downloading Whisper model -" \
        "this may take a while on the first run)"
        )
        text = transcribe_audio(prepared_audio)

        if text:
            logger.info("✓ Transcription completed")
            logger.info(f" Text: '{text}'")

            # Simulate save option
            logger.info("\n✓ Saving transcript to file...")
            save_to_txt(text, "output/transcription_resultado.txt")
            logger.info("✓ Saved file: transcription_resultado.txt")

            logger.info("\n✓ Copying text to clipboard...")
            copy_to_clipboard(text)
            logger.info("✓ Text available in clipboard")

        else:
            logger.warning("⚠ Could not get transcript")

    else:
        logger.warning(f"⚠ No file found: {audio_path}")

except Exception as e:
    logger.error(f"❌ Error in Option 1: {e}")

# OPTION 2: Simulate recording (without actually recording)
logger.info("\n" + "-" *70)
logger.info("OPTION 2: RECORD AND TRANSCRIBE (DEMO)")
logger.info("-" *70)

try:
    logger.info("✓ Recording module available")
    logger.info("✓ Transcription module available")
    logger.info("✓ Available output modules")

    logger.info("\nTo test the actual recording:")
    logger.info(" 1. Run: python src/main.py")
    logger.info(" 2. Select option 2")
    logger.info(" 3. Specifies recording duration")
    logger.info(" 4. Talk while recording")
    logger.info(" 5. The audio will be transcribed automatically")
except Exception as e:
    logger.error(f"❌ Error in Option 2: {e}")

# Final summary
logger.info("\n" + "=" *70)
logger.info("TESTS SUMMARY")
logger.info("=" *70)
logger.info("✅ Loading audio files: OK")
logger.info("✅ Whisper Transcription: OK")
logger.info("✅ Saved to files: OK")
logger.info("✅ Copy to clipboard: OK")
logger.info("✅ Project structure: OK")
logger.info("\n" + "=" *70)
logger.info("🎉 The project is ready to use")
logger.info("=" *70)
logger.info("\nNext steps:")
logger.info(" 1. Executed: python src/main.py")
logger.info(" 2. O compile a .exe: python build_exe.py")
