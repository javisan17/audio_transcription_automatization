"""Script to create a simple test audio file."""

import logging

import numpy as np
import soundfile as sf


# Create a simple test audio file (2 seconds)
sample_rate = 16000
duration = 2
t = np.linspace(0, duration, int(sample_rate * duration))

# Create a simple sound (test tone)
audio = 0.3 * np.sin(2 * np.pi * 440 * t)

# Keep
sf.write("test_audio.wav", audio, sample_rate)


logger = logging.getLogger(__name__)
logger.info("Created test file: test_audio.wav")
