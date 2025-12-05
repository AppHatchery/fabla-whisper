# Fabla Whisper Transcription Tool

A Python tool that uses OpenAI's Whisper model to transcribe audio files from a selected folder.

**Fabla** - Audio diary and EMA data collection: [fabla.framer.website](https://fabla.framer.website)

## Features

- Supports multiple audio formats: WAV, MP3, AAC, M4A, FLAC, OGG, WMA
- Interactive folder selection dialog
- Automatically creates output folder in Downloads with naming: `original_folder_name_transcripts`
- Saves transcripts as CSV file
- Console output showing transcription progress and summary

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

3. **Install tkinter (usually included with Python, but if needed):**

   - **macOS:** Usually pre-installed with Python
   - **Linux (Ubuntu/Debian):**
     ```bash
     sudo apt-get install python3-tk
     ```
   - **Windows:** Usually pre-installed with Python

## Usage

1. Run the script:
   ```bash
   python transcribe-whisper.py
   ```

2. A folder selection dialog will appear - select the folder containing your audio files

3. The script will:
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

## Notes

- The script uses the "base" Whisper model by default. You can change this in the code to "tiny", "small", "medium", or "large" for different accuracy/speed tradeoffs
- Larger models provide better accuracy but are slower
- The first run will download the Whisper model (this may take a few minutes)

