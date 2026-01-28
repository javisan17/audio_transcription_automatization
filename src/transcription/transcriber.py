# src/transcription/transcriber.py

import whisper
from typing import Optional
import numpy as np
import soundfile as sf
import os
import threading
import time


def transcribe_audio(audio_path: str, model: str = "small") -> Optional[str]:
    """
    Transcribe un archivo de audio usando Whisper.
    Soporta archivos wav, mp3, m4a, flac, ogg, mp4.
    Retorna el texto transcrito o None si hay error.
    """
    
    result = [None]
    exception = [None]
    
    def transcribe_worker():
        try:
            print(f"Cargando modelo Whisper ({model})...")
            whisper_model = whisper.load_model(model)
            
            print(f"Transcribiendo audio: {audio_path}")
            
            # Intentar transcribir directamente con Whisper (soporta múltiples formatos)
            try:
                result[0] = whisper_model.transcribe(audio_path, language="es", verbose=False)
                text = result[0].get("text", "").strip()
                if text:
                    print("Transcripción completada.")
                    result[0] = text
                else:
                    print("Advertencia: No se detectó texto en el audio")
                    result[0] = "No se detectó contenido de audio"
            
            except Exception as e:
                print(f"Intento 1 falló: {e}")
                print("Intentando método alternativo...")
                
                # Si falla, intentamos cargar el audio directamente con soundfile
                try:
                    audio_data, sr = sf.read(audio_path)
                    
                    # Convertir a float32
                    audio_data = audio_data.astype(np.float32)
                    
                    # Convertir a mono si es estéreo
                    if len(audio_data.shape) > 1:
                        audio_data = np.mean(audio_data, axis=1)
                        
                    # Normalizar si es necesario
                    max_val = np.abs(audio_data).max()
                    if max_val > 1.0:
                        audio_data = audio_data / max_val
                    
                    # Resamplear a 16kHz si es necesario
                    if sr != 16000:
                        num_samples = int(len(audio_data) * 16000 / sr)
                        indices = np.linspace(0, len(audio_data)-1, num_samples)
                        audio_data = np.interp(indices, np.arange(len(audio_data)), audio_data)
                    
                    # Transcribir el audio en formato numpy
                    result[0] = whisper_model.transcribe(audio_data, language="es", verbose=False)
                    text = result[0].get("text", "").strip()
                    if text:
                        print("Transcripción completada (método alternativo).")
                        result[0] = text
                    else:
                        print("Advertencia: No se detectó texto en el audio")
                        result[0] = "No se detectó contenido de audio"
                    
                except Exception as e2:
                    print(f"Método alternativo también falló: {e2}")
                    result[0] = None
        
        except Exception as e:
            print(f"Error fatal al transcribir: {e}")
            import traceback
            traceback.print_exc()
            result[0] = None
    
    # Ejecutar con timeout
    thread = threading.Thread(target=transcribe_worker, daemon=True)
    thread.start()
    thread.join(timeout=300)  # 5 minutos timeout
    
    if thread.is_alive():
        print("Transcripción timeout excedido (5 minutos)")
        return None
    
    return result[0]
