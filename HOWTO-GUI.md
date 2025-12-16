## Fabla Whisper GUI – How To Run

This guide explains how to launch the **Fabla Whisper Transcription** GUI on macOS and use it to create CSV transcripts from audio folders.

### 1. Requirements

- **Operating system**: macOS (Apple Silicon or Intel)
- **Python**: 3.11+ (recommended: official installer from `python.org`)
- **FFmpeg** (required for audio decoding)
- **Python packages**:
  - `openai-whisper`
  - `pandas`
  - `tkinterdnd2`

#### Install FFmpeg (macOS)

If you use Homebrew:

```bash
brew install ffmpeg
```

You only need to do this once per machine.

---

### 2. One‑Time Setup (Recommended)

These steps create a dedicated virtual environment for Fabla Whisper so it doesn’t affect other projects.

From Terminal:

```bash
# Navigate to the project folder (adjust path as needed)
cd ~/fabla-whisper

# Create a virtualenv named "fabla-whisper" using Python 3.11
# Note: Adjust the Python path if your Python 3.11 is installed elsewhere
python3 -m venv fabla-whisper

# Activate the environment
source fabla-whisper/bin/activate

# Upgrade tooling
python -m pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -r requirements.txt

# Install Whisper and drag-and-drop support
pip install openai-whisper tkinterdnd2
```

You only need to create and populate the `fabla-whisper` environment once.  
Later sessions just need the **activation** step.

---

### 3. Launching the GUI

Every time you want to use the app:

```bash
# Navigate to the project folder
cd ~/fabla-whisper

# Activate the virtual environment
source fabla-whisper/bin/activate

# Launch the GUI
python transcribe-whisper-gui.py
```

The **Fabla Whisper Transcription** window will open.

---

### 4. Using the GUI

1. **Select a folder of audio files**
   - Drag & drop the folder into the **“Drop Folder Here”** card, **or**
   - Click **Select Folder** and choose the folder.

2. **Choose file type**
   - In **File type**, pick:
     - `All (.wav, .mp3, .aac)` (default), or
     - `.wav only`, `.mp3 only`, or `.aac only`.

3. **(Optional) Adjust filename format**
   - If your files follow the default pattern `ID_date_time.ext` (e.g. `P001_2024-01-15_14-30-00.wav`), you can leave the defaults.
   - Otherwise, set:
     - **Delimiter** (e.g. `_`)
     - **ID Position**, **Date Position**, **Time Position** (0‑based indexes after splitting on the delimiter).

4. **Start transcription**
   - Click **🎧  Start Transcription**.
   - The **Progress** section shows:
     - Model loading
     - Each file being transcribed
     - Any errors (e.g. FFmpeg not installed)

5. **Output**
   - When finished, a `transcripts.csv` file is saved **inside the folder you selected**.
   - Columns:
     - `Filename`
     - `Participant ID`
     - `Date`
     - `Time`
     - `Transcript`

---

### 5. Common Issues

- **FFmpeg not found**
  - Install via Homebrew: `brew install ffmpeg`
  - Re‑launch the GUI; the status box should say “FFmpeg detected – audio processing ready”.

- **Whisper download is slow**
  - The first run downloads the Whisper model; this is normal and only happens once.

- **No files transcribed**
  - Check:
    - File extensions match the selected **File type**
    - Folder actually contains `.wav`, `.mp3`, or `.aac` files

---

### 6. Exiting

- Close the GUI window.
- In Terminal, deactivate the environment:

```bash
deactivate
```

You can reactivate later with:

```bash
cd ~/fabla-whisper
source fabla-whisper/bin/activate
```


