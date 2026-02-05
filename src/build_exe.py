#!/usr/bin/env python3

"""Script to compile the application to .exe executable using PyInstaller.

Usage: python build_exe.py
IMPORTANT: Only works on Windows.
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

from logger import get_logger, setup_logging


setup_logging()
logger = get_logger(__name__)


def main():
    """Compile the application to an .exe executable using PyInstaller."""
    # Verify that it is running on Windows
    if platform.system() != "Windows":
        logger.error("BUG: This script only works on Windows")
        logger.info(f"   System detected: {platform.system()}")
        return 1

    # Compile by default console (CLI mode). Pass --windowed for window.
    console_build = True
    if "--windowed" in sys.argv:
        console_build = False

    root_dir = Path(__file__).parent.parent

    logger.info("=" * 60)
    logger.info("COMPILING EXECUTABLE -AUDIO TRANSCRIPT")
    logger.info("=" * 60)

    # Clean up previous builds
    logger.info("\n[1/2] Cleaning up previous builds..")
    for folder in [root_dir / "dist", root_dir / "build", root_dir / "__pycache__"]:
        if folder.exists():
            shutil.rmtree(folder)
            logger.info(f"   Deleted {folder.name}")

    # Compile with PyInstaller
    logger.info("\n[2/2] Compiling with PyInstaller...")
    logger.info(" (This may take several minutes)\n")

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

    # Window vs console
    if console_build:
        cmd.append("--console")
    else:
        cmd.append("--windowed")

    # Use absolute path to GUI script
    cmd.append(str(root_dir / "src" / "gui" / "gui_app.py"))

    result = subprocess.run(cmd, cwd=root_dir)

    if result.returncode == 0:
        exe_path = root_dir / "dist" / "AutoTranscriberAudio.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            logger.info("\n" + "=" * 60)
            logger.info(f"SUCCESS: {exe_path.name} created")
            logger.info(f"   Size: {size_mb:.1f} MB")
            logger.info(f"   Location: {exe_path}")
            logger.info("=" * 60)
            return 0

    logger.error("\nCompilation error")
    return 1


if __name__ == "__main__":
    sys.exit(main())
