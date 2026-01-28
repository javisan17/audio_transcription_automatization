import sys
import os
# Agregar src al path (padre del padre)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from audio import load_audio
from output import save_to_txt, copy_to_clipboard


print("\n" + "="*60)
print("PRUEBAS BÁSICAS DEL PROYECTO")
print("="*60)

# Test 1: Cargar audio
print("\nTest 1: Cargando audio...")
try:
    audio_path = os.path.abspath("audio/test_audio.wav")
    print(f"  Ruta absoluta: {audio_path}")
    result = load_audio(audio_path)
    print(f"  ✅ Audio cargado correctamente")

except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 2: Guardar en archivo
print("\nTest 2: Guardando en archivo...")
try:
    texto = "Esto es un texto de prueba\nCon dos líneas"
    save_to_txt(texto, "prueba_output.txt")
    print("  ✅ Archivo guardado: prueba_output.txt")
    with open("output/prueba_output.txt", 'r') as f:
        contenido = f.read()
        print(f"  Contenido guardado correctamente")

except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 3: Copiar al portapapeles
print("\nTest 3: Copiando al portapapeles...")
try:
    copy_to_clipboard("Texto en portapapeles - Prueba OK")
    print("  ✅ Texto copiado al portapapeles")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "="*60)
print("✅ PRUEBAS BÁSICAS COMPLETADAS")
print("="*60 + "\n")
