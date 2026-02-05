"""Módulo principal para la automatización de audio."""

from logger import get_logger, setup_logging


setup_logging()
logger = get_logger(__name__)

from options import opcion_1_transcribir_archivo, opcion_2_grabar_y_transcribir


def main():
    """Función principal del programa de automatización de audio."""
    logger.info("=" * 50)
    logger.info("AUTOMATIZACIÓN DE AUDIO - TRANSCRIPCIÓN")
    logger.info("=" * 50)

    while True:
        logger.info("\nElige una opción:")
        logger.info("1 - Transcribir un archivo de audio")
        logger.info("2 - Grabar audio y transcribir")
        logger.info("3 - Salir")

        opcion = input("\nOpción (1/2/3): ").strip()

        if opcion == "1":
            opcion_1_transcribir_archivo()
        elif opcion == "2":
            opcion_2_grabar_y_transcribir()
        elif opcion == "3":
            logger.info("\n¡Hasta luego!")
            break
        else:
            logger.warning("Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    main()
