import os
from audio import record_audio
from transcription import transcribe_audio
from output import copy_to_clipboard, save_to_txt



def opcion_2_grabar_y_transcribir():
    """
    Graba audio en tiempo real y lo transcribe.
    """

    print("\n=== OPCIÓN 2: Grabar y Transcribir ===")
    
    # Pedir duración
    try:
        duracion = int(input("¿Cuántos segundos quieres grabar? (default: 30): ").strip() or "30")

    except ValueError:
        print("❌ Debes ingresar un número válido.")
        return
    
    # Grabar
    audio_grabado = record_audio(duration=duracion)
    if not audio_grabado:
        print("❌ Error en la grabación.")
        return
    
    # Transcribir
    texto = transcribe_audio(audio_grabado)
    if not texto:
        print("❌ Error en la transcripción.")
        return
    
    # Mostrar texto
    print(f"\n📝 Texto transcrito:\n{texto}\n")
    
    # Preguntar dónde guardar
    opcion_salida = input("¿Dónde quieres guardar? (1=Portapapeles, 2=Archivo .txt): ").strip()
    
    if opcion_salida == "1":
        copy_to_clipboard(texto)
        print("✅ Texto copiado al portapapeles.")
    elif opcion_salida == "2":
        nombre_archivo = input("Nombre del archivo (default: transcripcion.txt): ").strip()
        nombre_archivo = nombre_archivo or "transcripcion.txt"
        save_to_txt(texto, nombre_archivo)
        print(f"✅ Texto guardado en {nombre_archivo}")
    else:
        print("❌ Opción no válida.")
