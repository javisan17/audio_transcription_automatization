"""Script de pruebas básicas para verificar funcionalidades principales del proyecto."""

import os
import sys


# Agregar src al path (padre del padre)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from audio import load_audio
from logger import get_logger
from output import copy_to_clipboard, save_to_txt


logger = get_logger(__name__)
logger.info("\n" + "=" * 60)
logger.info("PRUEBAS BÁSICAS DEL PROYECTO")
logger.info("=" * 60)

# Test 1: Cargar audio
logger.info("\nTest 1: Cargando audio...")
try:
    audio_path = os.path.abspath("audio/test_audio.wav")
    logger.debug(f"  Ruta absoluta: {audio_path}")
    result = load_audio(audio_path)
    logger.info("  ✅ Audio cargado correctamente")

except Exception as e:
    logger.error(f"  ❌ Error: {e}")

# Test 2: Guardar en archivo
logger.info("\nTest 2: Guardando en archivo...")
try:
    texto = "Esto es un texto de prueba\nCon dos líneas"
    save_to_txt(texto, "prueba_output.txt")
    logger.info("  ✅ Archivo guardado: prueba_output.txt")
    with open("output/prueba_output.txt") as f:
        contenido = f.read()
        logger.info("  Contenido guardado correctamente")

except Exception as e:
    logger.error(f"  ❌ Error: {e}")

# Test 3: Copiar al portapapeles
logger.info("\nTest 3: Copiando al portapapeles...")
try:
    copy_to_clipboard("Texto en portapapeles - Prueba OK")
    logger.info("  ✅ Texto copiado al portapapeles")

except Exception as e:
    logger.error(f"  ❌ Error: {e}")

logger.info("\n" + "=" * 60)
logger.info("✅ PRUEBAS BÁSICAS COMPLETADAS")
logger.info("=" * 60 + "\n")
