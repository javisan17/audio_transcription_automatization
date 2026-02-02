"""Script para crear un archivo de audio de prueba simple."""

import numpy as np
import soundfile as sf


# Crear un archivo de audio de prueba simple (2 segundos)
sample_rate = 16000
duration = 2
t = np.linspace(0, duration, int(sample_rate * duration))

# Crear un sonido simple (tono de prueba)
audio = 0.3 * np.sin(2 * np.pi * 440 * t)

# Guardar
sf.write("test_audio.wav", audio, sample_rate)
print("✅ Archivo de prueba creado: test_audio.wav")
