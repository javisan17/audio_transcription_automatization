# 🎙️ Automatización de Audio - Transcripción con IA

Aplicación moderna para transcribir archivos de audio o grabar audio en tiempo real usando **OpenAI Whisper**.

## ✨ Características

### Opción 1: Transcribir Archivo
- Carga cualquier archivo de audio (.wav, .mp3, .m4a, .flac, .ogg, .mp4)
- Transcripción automática con Whisper
- Conversión automática de MP4 a WAV
- Interfaz amigable para seleccionar archivos

### Opción 2: Grabar y Transcribir ⭐ (NUEVO)
- **Modo 1: Duración fija** - Graba durante un tiempo específico (5-300 segundos)
- **Modo 2: Control manual** - Presiona START y STOP cuando quieras (NUEVO)
- Grabación de audio en tiempo real desde el micrófono
- Transcripción automática del audio grabado
- Indicadores de progreso en tiempo real

### Características Comunes
- ✅ Copiar transcripción al portapapeles
- ✅ Guardar transcripción en archivo .txt
- ✅ Interfaz gráfica intuitiva con Tkinter
- ✅ Mensajes de estado y errores claros
- ✅ Soporte multi-idioma (configurado para español)

## 🏗️ Estructura del Proyecto

```
audio/
├── src/
│   ├── main.py                 # Punto de entrada CLI
│   ├── audio/
│   │   ├── loader.py          # Carga y conversión de audio
│   │   ├── recorder.py        # Grabación de audio
│   │   └── __init__.py
│   ├── gui/
│   │   ├── gui_app.py         # Interfaz gráfica principal
│   │   └── __init__.py
│   ├── options/
│   │   ├── option1.py         # Opción 1: Transcribir archivo
│   │   ├── option2.py         # Opción 2: Grabar y transcribir
│   │   └── __init__.py
│   ├── output/
│   │   ├── clipboard.py       # Copiar al portapapeles
│   │   ├── text_file.py       # Guardar en archivo
│   │   └── __init__.py
│   ├── transcription/
│   │   ├── transcriber.py     # Transcripción con Whisper
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── tests/                      # Tests y ejemplos
├── pyproject.toml             # Configuración del proyecto
├── build_exe.py               # Script para compilar .exe
└── README.md                  # Este archivo
```

## 🚀 Instalación y Uso

### Requisitos Previos

- **Python 3.8+**
- **FFmpeg** (para conversión de audio)
  - Windows: Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html) o usa `choco install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`

### Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd audio
   ```

2. **Crear entorno virtual (opcional pero recomendado)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   # O si usas pyproject.toml:
   pip install -e .
   ```

### Uso - Interfaz Gráfica (GUI) ⭐ RECOMENDADO

```bash
python -m src.gui.gui_app
```

O simplemente haz doble clic en `AutoTranscriberAudio.exe` si ya compilaste el ejecutable.

### Uso - Línea de Comandos (CLI)

```bash
python -m src.main
```

Luego selecciona la opción deseada del menú interactivo.

## 🔨 Compilar Ejecutable (.exe)

### Requisito
Asegúrate de tener instalado PyInstaller:
```bash
pip install pyinstaller
```

### Compilación

Ejecuta el script de compilación:

```bash
python build_exe.py
```

**¿Qué hace?**
1. Limpia compilaciones anteriores
2. Prepara las dependencias
3. Compila la aplicación con PyInstaller
4. Genera un ejecutable en la carpeta `dist/`

### Resultado

Después de compilar, encontrarás:
```
dist/
└── AutoTranscriberAudio.exe
```

**Para distribuir:**
- Solo necesitas el archivo `.exe`
- No requiere Python instalado en el equipo destino
- Simplemente haz doble clic para ejecutar

## 📋 Opciones de Uso

### Opción 1: Transcribir Archivo
1. Haz clic en "Seleccionar archivo"
2. Elige un archivo de audio
3. Haz clic en "Transcribir archivo"
4. Espera a que se complete la transcripción
5. Copia al portapapeles o guarda como archivo

### Opción 2: Grabar y Transcribir

#### Modo 1: Duración Fija
1. Selecciona "Duración fija (segundos)"
2. Especifica cuántos segundos grabar (5-300)
3. Haz clic en "Grabar"
4. Habla al micrófono
5. Espera a que termine la grabación y transcripción

#### Modo 2: Control Manual (NUEVO)
1. Selecciona "Control manual (START/STOP)"
2. Haz clic en "🔴 Iniciar Grabación"
3. Habla al micrófono
4. Haz clic en "⏹️ Detener Grabación" cuando termines
5. Espera a que termine la transcripción

## 🔧 Configuración

### Modelos de Whisper Disponibles
En `transcriber.py`, puedes cambiar el modelo:
- `tiny` - Rápido pero menos preciso
- `base` - Buena relación velocidad/precisión
- `small` - Más preciso (por defecto)
- `medium` - Muy preciso
- `large` - Máxima precisión (muy pesado)

```python
# En src/transcription/transcriber.py
transcribe_audio(audio_path, model="small")  # Cambiar aquí
```

### Cambiar Idioma
```python
# En src/transcription/transcriber.py
result = whisper_model.transcribe(audio_path, language="es")  # "es" para español
```

## 🐛 Solución de Problemas

### "FFmpeg no encontrado"
**Solución:**
- Windows: Instala FFmpeg desde [ffmpeg.org](https://ffmpeg.org/download.html)
- Agrega FFmpeg a la variable de entorno PATH

### "No se captura audio"
**Soluciones:**
- Verifica que el micrófono esté conectado y activo
- En Configuración de Sonido, asegúrate que el micrófono sea el dispositivo de entrada
- Prueba otro dispositivo de grabación

### "Error de transcripción"
**Soluciones:**
- El audio podría ser muy silencioso - habla más fuerte
- El audio podría tener mucho ruido - encuentra un lugar tranquilo
- Intenta con un modelo más pequeño (cambia a `base` en lugar de `small`)

### "Archivo .exe muy grande"
- Esto es normal - incluye Python y todas las dependencias
- Tamaño típico: 400-600 MB

## 📚 Dependencias Principales

- **OpenAI Whisper** - Transcripción de voz a texto
- **SoundDevice** - Captura de audio del micrófono
- **SoundFile** - Procesamiento de archivos de audio
- **NumPy** - Cálculos numéricos
- **FFmpeg** - Conversión de formatos de audio
- **Tkinter** - Interfaz gráfica
- **PyPerclip** - Acceso al portapapeles
- **PyInstaller** - Compilación de ejecutables

## 📝 Notas Técnicas

### Grabación Manual
- Usa `sounddevice` con streaming de audio en tiempo real
- Captura continuamente mientras se presiona el botón START
- Convierte a WAV al presionar STOP
- Luego procesa como cualquier otro archivo

### Transcripción
- Utiliza modelos pre-entrenados de Whisper
- Resamplea automáticamente a 16 kHz
- Normaliza el audio si es necesario
- Soporta múltiples formatos de entrada

### Compilación
- PyInstaller empaqueta todo en un ejecutable
- Se incluyen todas las dependencias de Python
- El ejecutable funciona sin requerir Python instalado
- Primera ejecución puede ser más lenta mientras se extrae el contenido

## 🎯 Casos de Uso

- 📝 Transcribir entrevistas
- 🎓 Notas de clase
- 💼 Reuniones de trabajo
- 📱 Memos de voz
- 🎤 Podcasts y grabaciones
- 📚 Dictado de documentos

## 📄 Licencia

Proyecto personal para automatización de audio.

## 🤝 Contribuciones

¡Las mejoras son bienvenidas! Algunas ideas:
- Soporte para múltiples idiomas en la GUI
- Edición de transcripciones
- Exportación a múltiples formatos
- Historial de transcripciones
- Configuración de calidad de Whisper desde la GUI

## 📞 Soporte

Si encuentras problemas:
1. Revisa la sección "Solución de Problemas"
2. Asegúrate de tener todas las dependencias instaladas
3. Verifica que FFmpeg esté en el PATH del sistema
4. Prueba con un modelo más pequeño de Whisper

```bash
python src/main.py
```

### Compilar a .exe

```bash
python build_exe.py
```

El archivo .exe estará en la carpeta `dist/`

## Requisitos instalados

- openai-whisper
- ffmpeg-python
- sounddevice
- soundfile
- pyperclip
- pyinstaller
- numpy

## Notas

- El primer uso descargará el modelo de Whisper (base) automáticamente (~140MB)
- Puedes cambiar el modelo en transcriber.py si quieres más precisión (small, medium, large)
