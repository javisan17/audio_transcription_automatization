"""Configuración de pytest para el proyecto de automatización de audio."""

import os
import sys


# Asegurar que src esté en sys.path para poder importar `logger` en pruebas
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from logger import setup_logging


# Configurar logging centralizado para las pruebas
setup_logging()
