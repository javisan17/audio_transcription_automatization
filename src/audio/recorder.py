# src/audio/recorder.py

"""Gestión de grabación de audio en tiempo real."""

import tempfile
import threading

import numpy as np
import sounddevice as sd
import soundfile as sf

from logger import get_logger


logger = get_logger(__name__)


class AudioRecorder:
    """Grabador de audio con control de inicio/parada."""

    def __init__(self):
        """Inicializa el estado del grabador y el buffer de audio."""
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 16000
        self.thread = None

    def start_recording(self):
        """Inicia la grabación de audio."""
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_data = []

        import logging
        logger = logging.getLogger(__name__)
        logger.info("Iniciando grabación... (presiona STOP en la GUI para detener)")

        # Iniciar grabación en un hilo separado
        self.thread = threading.Thread(target=self._record_stream, daemon=True)
        self.thread.start()

    def _record_stream(self):
        """Stream de grabación continua."""
        try:
            # Verificar dispositivos
            devices = sd.query_devices()
            input_devices = [
                i for i, dev in enumerate(devices) if dev["max_input_channels"] > 0
            ]

            if not input_devices:
                logger.warning("No se encontraron dispositivos de entrada de audio.")
                self.is_recording = False
                return

            device = None  # Por defecto

            # Usar stream para grabación continua
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.debug(f"Estado del stream: {status}")
                # Copiar datos de audio
                self.audio_data.append(indata.copy())

            # Crear stream de audio
            with sd.InputStream(
                callback=audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=4096,
                device=device,
            ):
                # Grabar mientras is_recording sea True
                while self.is_recording:
                    sd.sleep(100)  # Pequeña pausa para no consumir CPU

        except Exception as e:
            logger.exception(f"Error durante la grabación: {e}")
            self.is_recording = False

    def stop_recording(self) -> str:
        """Detiene la grabación y retorna la ruta del archivo WAV."""
        if not self.is_recording:
            return None

        self.is_recording = False

        # Esperar a que termine el thread
        if self.thread:
            self.thread.join(timeout=2)

        logger.info("Grabación detenida")

        if not self.audio_data:
            logger.warning("No se grabó audio")
            return None

        # Concatenar todos los bloques de audio
        audio_array = np.concatenate(self.audio_data, axis=0)

        # Convertir a float32
        audio_array = audio_array.astype(np.float32)

        # Normalizar si es necesario
        max_val = np.abs(audio_array).max()
        if max_val > 1.0:
            audio_array = audio_array / max_val

        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_wav = temp_file.name
        sf.write(temp_wav, audio_array, self.sample_rate)

        logger.info(f"Audio guardado: {temp_wav}")
        return temp_wav


# Instancia global del grabador
global_recorder = AudioRecorder()


def start_recording() -> None:
    """Inicia la grabación de audio."""
    global_recorder.start_recording()


def stop_recording() -> str:
    """Detiene la grabación y retorna la ruta del archivo."""
    return global_recorder.stop_recording()


def record_audio(duration: int = 30, sample_rate: int = 16000) -> str:
    """Función legacy para compatibilidad.

    Graba audio durante un tiempo específico.
    """
    logger.info(f"Grabando durante {duration} segundos...")

    try:
        # Verificar dispositivos disponibles
        devices = sd.query_devices()
        input_devices = [
            i for i, dev in enumerate(devices) if dev["max_input_channels"] > 0
        ]

        if not input_devices:
            raise RuntimeError("No se encontraron dispositivos de entrada de audio.")

        # Usar el dispositivo por defecto o el primero disponible
        device = None  # Por defecto

        # Grabar audio
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32,
            device=device,
        )

        # Esperar a que termine la grabación
        sd.wait()

        # Verificar que se grabó algo
        if np.abs(audio_data).max() < 0.01:
            raise RuntimeError("No se detectó audio. Verifica el micrófono.")

        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_wav = temp_file.name
        sf.write(temp_wav, audio_data, sample_rate)

        logger.info(f"Grabación completada: {temp_wav}")
        return temp_wav

    except KeyboardInterrupt:
        logger.info("\nGrabación cancelada.")
        return None

    except Exception as e:
        logger.error(f"Error al grabar: {e}")
        return None
