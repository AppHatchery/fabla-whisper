# Fabla Whisper Transcription Tool

A Python tool that uses OpenAI's Whisper model to transcribe audio files from a selected folder.

**Fabla** - Audio diary and EMA data collection: [fabla.framer.website](https://fabla.framer.website)

## Features

- **GUI Version** with drag & drop folder support (recommended for non-technical users)
- **Command-line version** for automated workflows
- Supports multiple audio formats: WAV, MP3, AAC, M4A, FLAC, OGG, WMA
- Interactive folder selection dialog
- Automatically creates output folder in Downloads with naming: `original_folder_name_transcripts`
- Saves transcripts as CSV file
- Real-time progress bar and status updates
- Configurable filename format parsing

## Requirements

- Python 3.8 or higher
- macOS, Windows, or Linux

## Installation

1. **Install Python dependencies:**

   Using requirements.txt (recommended):
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install openai-whisper pandas
   ```

2. **Install FFmpeg (required for audio processing):**

   **Why FFmpeg?** Whisper uses FFmpeg internally to decode audio files (MP3, M4A, AAC, FLAC, etc.) into a format it can process. Without FFmpeg, Whisper cannot read most audio formats.
   
   - **macOS (using Homebrew):**
     ```bash
     brew install ffmpeg
     ```
   
   - **Windows:**
     Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
   
   - **Linux (Ubuntu/Debian):**
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   
   **Note:** The GUI version will check for FFmpeg on startup and display a warning if it's not found.

3. **Install tkinter (usually included with Python, but if needed):**

   - **macOS:** Usually pre-installed with Python
   - **Linux (Ubuntu/Debian):**
     ```bash
     sudo apt-get install python3-tk
     ```
   - **Windows:** Usually pre-installed with Python

## Usage

### GUI Version (Recommended)

1. Run the GUI version:
   ```bash
   python transcribe-whisper-gui.py
   ```

2. **Drag & drop** a folder with audio files onto the drop area, or click "Select Folder" to browse

3. (Optional) Adjust filename format settings if your files use a different format than the default

4. Click "Start Transcription"

5. The script will:
   - Process all audio files in the selected folder
   - Show real-time progress in the GUI
   - Create a folder in your Downloads directory named `original_folder_name_transcripts`
   - Save the transcripts to a CSV file called `transcripts.csv` in that folder
   - Display a completion message when done

### Command-Line Version

1. Run the script:
   ```bash
   python transcribe-whisper.py
   ```

2. A folder selection dialog will appear - select the folder containing your audio files

3. Configure filename format (or press Enter for default Fabla format)

4. The script will:
   - Process all audio files in the selected folder
   - Create a folder in your Downloads directory named `original_folder_name_transcripts`
   - Save the transcripts to a CSV file called `transcripts.csv` in that folder
   - Display progress and a summary in the console

## Output Format

The CSV file contains the following columns:
- `Filename`: Name of the audio file
- `Participant ID`: Extracted from filename (if formatted as `ID_date_time.ext`)
- `Date`: Extracted from filename (if formatted as `ID_date_time.ext`)
- `Time`: Extracted from filename (if formatted as `ID_date_time.ext`)
- `Transcript`: The transcribed text

## Creating a Standalone Executable

To share this tool with users who don't have Python installed, you can create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_executable.py
   ```

3. The executable will be created in the `dist/` folder

See [PACKAGING.md](PACKAGING.md) for detailed instructions and troubleshooting.

**Note**: Users will still need FFmpeg installed on their system for the executable to work.

## Notes

- The script uses the "base" Whisper model by default. You can change this in the code to "tiny", "small", "medium", or "large" for different accuracy/speed tradeoffs
- Larger models provide better accuracy but are slower
- The first run will download the Whisper model (this may take a few minutes)
- Drag & drop requires `tkinterdnd2` (included in requirements.txt). If not installed, users can use the "Select Folder" button instead

