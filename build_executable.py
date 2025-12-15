"""
Script to build a standalone executable using PyInstaller.
Run this script to create a distributable .app (macOS) or .exe (Windows) file.

Usage:
    python build_executable.py
"""

import subprocess
import sys
import os

def build_executable():
    """Build executable using PyInstaller."""
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Check if required dependencies are installed
    print("Checking dependencies...")
    required_packages = ['whisper', 'pandas', 'tkinterdnd2']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'whisper':
                __import__('whisper')
            elif package == 'tkinterdnd2':
                __import__('tkinterdnd2')
            else:
                __import__(package)
            print(f"  ✓ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"  ✗ {package} missing")
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}...")
        # Map package names to pip names
        pip_names = {
            'whisper': 'openai-whisper',
            'tkinterdnd2': 'tkinterdnd2',
            'pandas': 'pandas'
        }
        packages_to_install = [pip_names.get(pkg, pkg) for pkg in missing_packages]
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages_to_install)
        print("Dependencies installed successfully!")
    
    # Check if spec file exists, use it if available
    spec_file = "Fabla-Whisper-Transcription.spec"
    use_spec = os.path.exists(spec_file)
    
    if use_spec:
        print(f"Using spec file: {spec_file}")
        cmd = ["pyinstaller", "--clean", spec_file]
    else:
        # PyInstaller command
        cmd = [
            "pyinstaller",
            "--name=Fabla-Whisper-Transcription",
            "--onefile",
            "--windowed",  # No console window (GUI only)
            "--clean",  # Clean cache before building
            "--hidden-import=whisper",  # Explicitly include whisper
            "--hidden-import=whisper.model",  # Include whisper model
            "--hidden-import=whisper.audio",  # Include whisper audio processing
            "--hidden-import=whisper.decoding",  # Include whisper decoding
            "--hidden-import=whisper.normalizers",  # Include whisper normalizers
            "--hidden-import=whisper.tokenizer",  # Include whisper tokenizer
            "--hidden-import=whisper.utils",  # Include whisper utils
            "--hidden-import=whisper.transcribe",  # Include whisper transcribe
            "--hidden-import=ffmpeg",  # Include ffmpeg-python if used
            "--hidden-import=numpy",  # Ensure numpy is included
            "--hidden-import=torch",  # Ensure torch is included
            "--hidden-import=torchaudio",  # Ensure torchaudio is included
            "transcribe-whisper-gui.py"
        ]
        
        # macOS specific: create .app bundle
        if sys.platform == "darwin":
            cmd.extend([
                "--osx-bundle-identifier=com.fabla.whisper",
            ])
    
    print("Building executable...")
    print("Command:", " ".join(cmd))
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "="*60)
        print("Build complete!")
        print("="*60)
        print("\nExecutable location:")
        if sys.platform == "darwin":
            print("  dist/Fabla-Whisper-Transcription.app")
        elif sys.platform == "win32":
            print("  dist/Fabla-Whisper-Transcription.exe")
        else:
            print("  dist/Fabla-Whisper-Transcription")
        print("\nYou can now distribute this executable to users.")
        print("Note: The first run may take longer as it loads the Whisper model.")
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()

