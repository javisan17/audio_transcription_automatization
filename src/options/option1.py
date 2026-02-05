# src/options/option1.py

"""Módulo para la gestión de la opción 1 (transcripción de un archivo)."""

import os

from audio import load_audio
from logger import get_logger
from output import copy_to_clipboard, save_to_txt
from transcription import transcribe_audio


logger = get_logger(__name__)


def opcion_1_transcribir_archivo():
    """Transcribe un archivo de audio existente."""
    logger.info("\n=== OPCIÓN 1: Transcribir Archivo ===")
    archivo = input("Ingresa la ruta al archivo de audio: ").strip()

    if not os.path.isfile(archivo):
        logger.warning("El archivo no existe.")
        return

    # Cargar y preparar audio
    audio_preparado = load_audio(archivo)

    # Transcribir
    texto = transcribe_audio(audio_preparado)
    if not texto:
        logger.error("Error en la transcripción.")
        return

    # Mostrar texto
    logger.info(f"\nTexto transcrito:\n{texto}\n")

    # Preguntar dónde guardar
    opcion_salida = input(
        "¿Dónde quieres guardar? (1=Portapapeles, 2=Archivo .txt): "
    ).strip()

    if opcion_salida == "1":
        copy_to_clipboard(texto)
        logger.info("Texto copiado al portapapeles.")

    elif opcion_salida == "2":
        nombre_archivo = input(
            "Nombre del archivo (default: transcripcion.txt): "
        ).strip()
        nombre_archivo = nombre_archivo or "transcripcion.txt"
        save_to_txt(texto, nombre_archivo)
        logger.info(f"Texto guardado en {nombre_archivo}")
        
    else:
        logger.warning("Opción no válida.")