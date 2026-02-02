# src/audio/loader.py

"""Utilidades para la conversión y validación de formatos de audio."""

import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import suppress


SUPPORTED_EXTENSIONS = (".wav", ".mp3", ".m4a", ".flac", ".ogg", ".mp4")


def check_ffmpeg_installed() -> bool:
    """Verifica si FFmpeg está instalado y disponible en el PATH."""
    try:
        # En Windows buscar ffmpeg.exe, en otros sistemas ffmpeg
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return result.returncode == 0

    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_ffmpeg_path() -> str:
    """Obtiene la ruta completa de FFmpeg.

    En Windows, busca en paths comunes.
    """
    # Primero intentar encontrar ffmpeg en el PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    # En Windows, búsqueda adicional en rutas comunes
    if sys.platform.startswith("win"):
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            os.path.expanduser(r"~\ffmpeg\bin\ffmpeg.exe"),
        ]
        for path in common_paths:
            if os.path.isfile(path):
                return path

    return None


def convert_mp4_to_wav(mp4_path: str) -> str:
    """Convierte un archivo MP4 a WAV usando ffmpeg.

    Retorna la ruta del archivo WAV temporal.
    """
    temp_wav = None

    try:
        # Verificar que el archivo de entrada existe
        if not os.path.isfile(mp4_path):
            raise FileNotFoundError(f"El archivo MP4 no existe: {mp4_path}")

        # Crear archivo temporal WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_wav = temp_file.name

        print(f"Convirtiendo MP4 a WAV: {mp4_path}")
        print(f"Archivo temporal: {temp_wav}")

        # Verificar si FFmpeg está disponible
        ffmpeg_path = get_ffmpeg_path()

        if not ffmpeg_path:
            raise RuntimeError(
                "FFmpeg no está instalado o no se encuentra en el PATH.\n\n"
                "Para Windows:\n"
                "1. Descarga FFmpeg desde: https://ffmpeg.org/download.html#build-windows\n"
                "2. Extrae el archivo ZIP\n"
                "3. Agrega la carpeta 'bin' al PATH del sistema\n"
                "   O copia ffmpeg.exe a: C:\\ffmpeg\\bin\\\n\n"
                "Después ejecuta: uv sync"
            )

        # Preparar comando con rutas correctas
        # En Windows, usar comillas en las rutas que contienen espacios
        cmd = [
            ffmpeg_path,
            "-i",
            mp4_path,
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-y",
            temp_wav,
        ]

        print(f"Ejecutando: {' '.join(cmd)}")

        # Ejecutar FFmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos
        )

        if result.returncode != 0:
            # Limpiar archivo temporal si hay error
            if os.path.exists(temp_wav):
                with suppress(OSError):
                    os.remove(temp_wav)

            error_msg = result.stderr if result.stderr else "Error desconocido"
            raise RuntimeError(
                f"FFmpeg error (código {result.returncode}): {error_msg}"
            )

        # Verificar que se generó el archivo
        if not os.path.exists(temp_wav):
            raise RuntimeError("El archivo WAV no fue generado (archivo no encontrado)")

        file_size = os.path.getsize(temp_wav)
        if file_size == 0:
            raise RuntimeError("El archivo WAV está vacío (0 bytes)")

        print(f"Conversión completada: {temp_wav} ({file_size} bytes)")
        return temp_wav

    except Exception as e:
        # Limpiar archivo temporal en caso de error
        if temp_wav and os.path.exists(temp_wav):
            with suppress(OSError):
                    os.remove(temp_wav)
        raise RuntimeError(f"Error al convertir MP4 a WAV: {str(e)}") from e


def load_audio(audio_path: str) -> str:
    """Valida un archivo de audio.
    
    Si es MP4, lo convierte a WAV automáticamente.
    Devuelve la ruta absoluta al audio.
    """
    # Convertir a ruta absoluta si es relativa
    audio_path = os.path.abspath(audio_path)

    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"No existe el archivo: {audio_path}")

    ext = os.path.splitext(audio_path)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato de audio no soportado. Extensión detectada: {ext}")

    # Si es MP4, convertir a WAV
    if ext == ".mp4":
        print("Archivo MP4 detectado, convirtiendo a WAV...")
        return convert_mp4_to_wav(audio_path)

    return audio_path
