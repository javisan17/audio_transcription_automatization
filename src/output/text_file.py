# src/output/text_file.py

"""Módulo para la exportación de transcripciones a archivos de texto."""

def save_to_txt(text, filename="transcripcion.txt"):
    """Guarda el texto transcrito en un archivo de texto."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)