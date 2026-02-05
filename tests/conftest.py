"""Pytest configuration for the audio automation project."""

import os
import sys


# Make sure src is in sys.path so you can import `logger` in tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from logger import setup_logging


# Configure centralized logging for testing
setup_logging()
