# Packaging Instructions for Fabla Whisper Transcription Tool

This guide explains how to create a standalone executable that can be shared with users who don't have Python installed.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **All dependencies** installed (run `pip install -r requirements.txt`)
3. **FFmpeg** installed (required for Whisper to work)

## Method 1: Using the Build Script (Recommended)

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_executable.py
   ```

3. The executable will be created in the `dist/` folder:
   - **macOS**: `dist/Fabla-Whisper-Transcription.app`
   - **Windows**: `dist/Fabla-Whisper-Transcription.exe`
   - **Linux**: `dist/Fabla-Whisper-Transcription`

## Method 2: Manual PyInstaller Command

### macOS
```bash
pyinstaller --name=Fabla-Whisper-Transcription \
            --onefile \
            --windowed \
            --osx-bundle-identifier=com.fabla.whisper \
            transcribe-whisper-gui.py
```

### Windows
```bash
pyinstaller --name=Fabla-Whisper-Transcription ^
            --onefile ^
            --windowed ^
            transcribe-whisper-gui.py
```

### Linux
```bash
pyinstaller --name=Fabla-Whisper-Transcription \
            --onefile \
            transcribe-whisper-gui.py
```

## Important Notes

### File Size
The executable will be large (200-500 MB) because it includes:
- Python interpreter
- Whisper model files
- All dependencies

### First Run
The first time a user runs the executable, it may take a few minutes to:
- Extract temporary files
- Download the Whisper model (if not bundled)

### FFmpeg Dependency
**Important**: Users still need FFmpeg installed on their system for the executable to work. The executable cannot bundle FFmpeg due to licensing.

**For macOS users:**
- Install via Homebrew: `brew install ffmpeg`
- Or download from: https://ffmpeg.org/download.html

**For Windows users:**
- Download from: https://ffmpeg.org/download.html
- Add to PATH or place in same folder as executable

**For Linux users:**
- Install via package manager: `sudo apt install ffmpeg` (Ubuntu/Debian)

### Distribution Options

1. **Direct Distribution**: Share the executable file directly
2. **DMG (macOS)**: Create a disk image with the .app file
3. **Installer (Windows)**: Use tools like Inno Setup or NSIS to create an installer
4. **Zip Archive**: Compress the executable and include a README with FFmpeg installation instructions

## Troubleshooting

### "Module not found" errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Try adding `--hidden-import` flags for missing modules

### Large file size
- This is normal - the executable includes Python and all dependencies
- Consider using `--onedir` instead of `--onefile` for faster startup (but requires distributing a folder)

### Drag & drop not working
- Make sure `tkinterdnd2` is installed: `pip install tkinterdnd2`
- Users can still use the "Select Folder" button if drag & drop doesn't work

## Alternative: Create a Simple Launcher Script

If packaging is too complex, you can create a simple launcher script that users can double-click:

### macOS (create `run.sh`):
```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 transcribe-whisper-gui.py
```

Make it executable: `chmod +x run.sh`

### Windows (create `run.bat`):
```batch
@echo off
cd /d "%~dp0"
python transcribe-whisper-gui.py
pause
```

Users would still need Python installed, but this is simpler than packaging.

