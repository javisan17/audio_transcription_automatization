# Audio Transcriber Automation (Whisper IA)

A Python-based tool for automated audio transcription using OpenAI's Whisper models. It supports processing existing files or recording in real-time via a GUI (Tkinter) or a CLI.

## Prerequisites

- **Python 3.8+**
- **FFmpeg**: Required for audio conversion and stream handling.
  - **Windows**: `choco install ffmpeg` or manual download from ffmpeg.org.
  - **Linux/macOS**: `sudo apt install ffmpeg` / `brew install ffmpeg`.

## Installation

This project is configured using `pyproject.toml`. Using a virtual environment is highly recommended:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies and project in editable mode
pip install -e .
```

## Usage

The application can be launched in two modes:

1. **Graphical User Interface (GUI)**:

```bash
python -m src.gui.gui_app
```

2. **Command Line Interface (CLI)**:

```bash
python -m src.main_console
```

**Key Features**

- **File Processing**: Transcribes `.mp3`, `.wav`, `.m4a`, `.flac` and `.mp4`.
- **Live Recording**:
  - _Timed mode_ (fixed duration).
  - _Manual control_ (Start/Stop).
- **Output**: Automatic export to `.txt` or direct clipboard copy.

## Configuration

### Model Configuration

The default model is set to `small`. To adjust precision or processing speed, modify the parameter in `src/transcription/transcriber.py`:

```python
# Available models: tiny, base, small, medium, large
transcribe_audio(audio_path, model="small")
```

`Note: The first execution will automatically download the selected model (ranging from ~150MB to 1GB+).`

### Change Lenguage

The default lenguage is set to `spanish`. To change the lenguage, modify the parameter in `src/transcription/transcriber.py`

```python
result = whisper_model.transcribe(audio_path, language="es", verbose=False)
```

## Building the Executable (.exe)

To generate a standalone Windows executable:

```bash
pip install pyinstaller
python src/build_exe.py
```

`Note: The final binary will be located in the dist/ folder.`

## License

Personal audio automation project
