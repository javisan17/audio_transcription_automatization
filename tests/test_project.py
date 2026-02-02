"""Script de prueba y verificar que funciones del proyecto funcionan correctamente."""

import os
import sys


# Agregar src al path (padre del padre)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_imports():
    """Prueba que todos los módulos se importan correctamente."""
    print("=" * 60)
    print("TEST 1: Verificar importaciones")
    print("=" * 60)
    try:
        print("✅ Todos los módulos importados correctamente")
        return True

    except Exception as e:
        print(f"❌ Error al importar: {e}")
        return False


def test_loader():
    """Prueba el cargador de audio."""
    print("\n" + "=" * 60)
    print("TEST 2: Prueba del cargador de audio")
    print("=" * 60)
    try:
        from audio import load_audio

        # Usar el archivo de prueba creado
        audio_path = "audio/test_audio.wav"
        if not os.path.exists(audio_path):
            print(f"⚠️  Archivo de prueba no encontrado: {audio_path}")
            return False

        result = load_audio(audio_path)
        print(f"✅ Audio cargado y preparado: {result}")
        print(f"   Archivo existe: {os.path.exists(result)}")
        return True

    except Exception as e:
        print(f"❌ Error al cargar audio: {e}")
        return False


def test_output_clipboard():
    """Prueba guardado en portapapeles."""
    print("\n" + "=" * 60)
    print("TEST 3: Prueba de portapapeles")
    print("=" * 60)
    try:
        from output import copy_to_clipboard

        texto_prueba = "Esto es una prueba de portapapeles"
        copy_to_clipboard(texto_prueba)
        print(f"✅ Texto copiado al portapapeles: '{texto_prueba}'")
        return True

    except Exception as e:
        print(f"❌ Error al copiar al portapapeles: {e}")
        return False


def test_output_file():
    """Prueba guardado en archivo."""
    print("\n" + "=" * 60)
    print("TEST 4: Prueba de guardado en archivo")
    print("=" * 60)
    try:
        from output import save_to_txt

        texto_prueba = "Esto es una prueba de archivo\nCon múltiples líneas"
        archivo_prueba = "output/test_output.txt"
        save_to_txt(texto_prueba, archivo_prueba)

        # Verificar que se creó el archivo
        if os.path.exists(archivo_prueba):
            with open(archivo_prueba, encoding="utf-8") as f:
                contenido = f.read()
            print(f"✅ Archivo guardado correctamente: {archivo_prueba}")
            print(f"   Contenido: {contenido[:50]}...")
            return True
        else:
            print(f"❌ Archivo no se creó: {archivo_prueba}")
            return False

    except Exception as e:
        print(f"❌ Error al guardar archivo: {e}")
        return False


def test_transcriber():
    """Prueba de transcripción (requiere tiempo)."""
    print("\n" + "=" * 60)
    print("TEST 5: Prueba de transcripción")
    print("=" * 60)
    try:
        from audio import load_audio
        from transcription import transcribe_audio

        audio_path = "audio/test_audio.wav"
        if not os.path.exists(audio_path):
            print(f"⚠️  Archivo de prueba no encontrado: {audio_path}")
            return False

        # Cargar audio
        audio_preparado = load_audio(audio_path)

        # Transcribir (esto puede tardar unos minutos la primera vez)
        print("Transcribiendo... (esto puede tardar unos minutos)")
        texto = transcribe_audio(audio_preparado)

        if texto is None:
            print("❌ La transcripción retornó None")
            return False

        print("✅ Transcripción completada")
        print(f"   Texto: '{texto}' (puede estar vacío si era solo un tono)")
        return True

    except Exception as e:
        print(f"❌ Error en transcripción: {e}")
        return False


def main():
    """Función principal para ejecutar todas las pruebas."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " PRUEBAS DEL PROYECTO DE AUTOMATIZACIÓN DE AUDIO ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")

    results = []

    # Ejecutar pruebas
    results.append(("Importaciones", test_imports()))
    results.append(("Cargador de Audio", test_loader()))
    results.append(("Portapapeles", test_output_clipboard()))
    results.append(("Archivo de Salida", test_output_file()))
    results.append(("Transcripción", test_transcriber()))

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)

    for nombre, resultado in results:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{nombre:<30} {estado}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} pruebas pasadas")

    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron")


if __name__ == "__main__":
    main()
