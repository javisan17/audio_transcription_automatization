# src/output/text_file.py

"""Module for exporting transcripts to text files."""

def save_to_txt(text, filename="transcripcion.txt"):
    """Save the transcribed text in a text file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)