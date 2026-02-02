"""Módulo principal para la automatización de audio."""

from options import opcion_1_transcribir_archivo, opcion_2_grabar_y_transcribir


def main():
    """Función principal del programa de automatización de audio."""
    print("=" * 50)
    print("🎙️  AUTOMATIZACIÓN DE AUDIO - TRANSCRIPCIÓN")
    print("=" * 50)

    while True:
        print("\nElige una opción:")
        print("1 - Transcribir un archivo de audio")
        print("2 - Grabar audio y transcribir")
        print("3 - Salir")

        opcion = input("\nOpción (1/2/3): ").strip()

        if opcion == "1":
            opcion_1_transcribir_archivo()
        elif opcion == "2":
            opcion_2_grabar_y_transcribir()
        elif opcion == "3":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    main()
