#!/usr/bin/env python3

"""Script para compilar la aplicación a ejecutable .exe usando PyInstaller.

Uso: python build_exe.py
IMPORTANTE: Solo funciona en Windows.
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    """Compila la aplicación a un ejecutable .exe usando PyInstaller."""
    # Verificar que se ejecuta en Windows
    if platform.system() != "Windows":
        print("ERROR: Este script solo funciona en Windows")
        print(f"   Sistema detectado: {platform.system()}")
        return 1

    # Compilar por consola por defecto (modo CLI). Pasar --windowed para ventana.
    console_build = True
    if "--windowed" in sys.argv:
        console_build = False

    root_dir = Path(__file__).parent

    print("=" * 60)
    print("COMPILANDO EJECUTABLE - TRANSCRIPCIÓN DE AUDIO")
    print("=" * 60)

    # Limpiar compilaciones anteriores
    print("\n[1/2] Limpiando compilaciones anteriores...")
    for folder in [root_dir / "dist", root_dir / "build", root_dir / "__pycache__"]:
        if folder.exists():
            shutil.rmtree(folder)
            print(f"   Eliminado {folder.name}")

    # Compilar con PyInstaller
    print("\n[2/2] Compilando con PyInstaller...")
    print("    (Esto puede tomar varios minutos)\n")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "AutoTranscriberAudio",
        "--paths",
        str(root_dir / "src"),
        "--collect-all",
        "sounddevice",
        "--collect-all",
        "soundfile",
        "--collect-all",
        "numpy",
        "--collect-all",
        "whisper",
        "--hidden-import=whisper",
        "--hidden-import=pyperclip",
        "--hidden-import=tkinter",
    ]

    # Ventana vs consola
    if console_build:
        cmd.append("--console")
    else:
        cmd.append("--windowed")

    cmd.append("src/gui/gui_app.py")

    result = subprocess.run(cmd, cwd=root_dir)

    if result.returncode == 0:
        exe_path = root_dir / "dist" / "AutoTranscriberAudio.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print(f"ÉXITO: {exe_path.name} creado")
            print(f"   Tamaño: {size_mb:.1f} MB")
            print(f"   Ubicación: {exe_path}")
            print("=" * 60)
            return 0

    print("\nError en la compilación")
    return 1


if __name__ == "__main__":
    sys.exit(main())
