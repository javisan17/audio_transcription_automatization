# src/options/option1.py

"""Módulo para la gestión de la opción 1 (transcripción de un archivo)."""

import os

from audio import load_audio
from output import copy_to_clipboard, save_to_txt
from transcription import transcribe_audio


def opcion_1_transcribir_archivo():
    """Transcribe un archivo de audio existente."""
    print("\n=== OPCIÓN 1: Transcribir Archivo ===")
    archivo = input("Ingresa la ruta al archivo de audio: ").strip()

    if not os.path.isfile(archivo):
        print("El archivo no existe.")
        return

    # Cargar y preparar audio
    audio_preparado = load_audio(archivo)

    # Transcribir
    texto = transcribe_audio(audio_preparado)
    if not texto:
        print("Error en la transcripción.")
        return

    # Mostrar texto
    print(f"\nTexto transcrito:\n{texto}\n")

    # Preguntar dónde guardar
    opcion_salida = input(
        "¿Dónde quieres guardar? (1=Portapapeles, 2=Archivo .txt): "
    ).strip()

    if opcion_salida == "1":
        copy_to_clipboard(texto)
        print("Texto copiado al portapapeles.")

    elif opcion_salida == "2":
        nombre_archivo = input(
            "Nombre del archivo (default: transcripcion.txt): "
        ).strip()
        nombre_archivo = nombre_archivo or "transcripcion.txt"
        save_to_txt(texto, nombre_archivo)
        print(f"Texto guardado en {nombre_archivo}")
        
    else:
        print("Opción no válida.")