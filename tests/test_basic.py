"""Basic test script to verify main functionalities of the project."""

import os
import sys


# Add src to path (parent of parent)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from audio import load_audio
from logger import get_logger
from output import copy_to_clipboard, save_to_txt


logger = get_logger(__name__)
logger.info("\n" + "=" * 60)
logger.info("BASIC PROJECT TESTS")
logger.info("=" * 60)

# Test 1: Load audio
logger.info("\nTest 1: Loading audio...")
try:
    audio_path = os.path.abspath("audio/test_audio.wav")
    logger.debug(f"  absolute path: {audio_path}")
    result = load_audio(audio_path)
    logger.info("  ✅ Audio loaded successfully")

except Exception as e:
    logger.error(f"  ❌ Error: {e}")

# Test 2: Save to file
logger.info("\nTest 2: Saving to file...")
try:
    texto = "This is a test text\With two lines"
    save_to_txt(texto, "prueba_output.txt")
    logger.info("  ✅ Saved file: prueba_output.txt")
    with open("output/prueba_output.txt") as f:
        contenido = f.read()
        logger.info("  Successfully saved content")

except Exception as e:
    logger.error(f"  ❌ Error: {e}")

# Test 3: Copy to clipboard
logger.info("\nTest 3: Copying to clipboard...")
try:
    copy_to_clipboard("Text on clipboard -Test OK")
    logger.info("  ✅ Text copied to clipboard")

except Exception as e:
    logger.error(f"  ❌ Error: {e}")

logger.info("\n" + "=" * 60)
logger.info("✅ BASIC TESTS COMPLETED")
logger.info("=" * 60 + "\n")
