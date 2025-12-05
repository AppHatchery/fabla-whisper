import os
import whisper
import pandas as pd
from pathlib import Path
from tkinter import filedialog, Tk

def select_folder():
    """Prompt the user to select a folder containing audio files."""
    root = Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring dialog to front
    
    folder_path = filedialog.askdirectory(title="Select folder containing audio files to transcribe")
    root.destroy()
    
    return folder_path

def get_downloads_folder():
    """Get the Downloads folder path for the current user."""
    home = Path.home()
    downloads = home / "Downloads"
    return downloads

def get_filename_format_config():
    """Prompt user to configure how to extract ID, date, and time from filenames."""
    print("\n" + "="*60)
    print("Filename Format Configuration")
    print("="*60)
    print("\nFabla audio files follow the format: PARTICIPANT_ID_DATE_TIME.extension")
    print("Example: P001_2024-01-15_14-30-00.wav")
    print("\nPress Enter to use the default format for Fabla audio files")
    print("(ID_date_time with '_' delimiter).")
    print("\nIf you want to use your own format, type 'custom':")
    
    choice = input("Choice [Enter for Fabla format / 'custom' for your own format]: ").strip().lower()
    
    if choice == 'custom':
        print("\nConfigure your filename format:")
        delimiter = input("Delimiter used to split filename parts (e.g., '_', '-', '.') [default: '_']: ").strip()
        delimiter = delimiter if delimiter else '_'
        
        print("\nWhich position in the filename contains each part?")
        print("(Positions start at 0. Example: 'ID_date_time.ext' split by '_' gives [0:ID, 1:date, 2:time])")
        
        id_pos = input("Participant ID position [default: 0]: ").strip()
        id_pos = int(id_pos) if id_pos.isdigit() else 0
        
        date_pos = input("Date position [default: 1]: ").strip()
        date_pos = int(date_pos) if date_pos.isdigit() else 1
        
        time_pos = input("Time position [default: 2]: ").strip()
        time_pos = int(time_pos) if time_pos.isdigit() else 2
        
        return {
            'delimiter': delimiter,
            'id_position': id_pos,
            'date_position': date_pos,
            'time_position': time_pos
        }
    else:
        # Default Fabla format: ID_date_time
        return {
            'delimiter': '_',
            'id_position': 0,
            'date_position': 1,
            'time_position': 2
        }

def extract_filename_info(filename, config):
    """
    Extract participant ID, date, and time from filename based on configuration.
    
    Args:
        filename: The audio filename
        config: Dictionary with delimiter and position information
    
    Returns:
        Tuple of (participant_id, date, time)
    """
    # Remove file extension
    name_without_ext = os.path.splitext(filename)[0]
    
    # Split by delimiter
    parts = name_without_ext.split(config['delimiter'])
    
    # Extract based on positions
    participant_id = parts[config['id_position']] if len(parts) > config['id_position'] else ""
    date = parts[config['date_position']] if len(parts) > config['date_position'] else ""
    time = parts[config['time_position']] if len(parts) > config['time_position'] else ""
    
    return participant_id, date, time

def transcribe_audio_files(input_folder, output_folder, filename_config):
    """Transcribe all audio files in the input folder."""
    # Load the Whisper model
    print("Loading Whisper model...")
    model = whisper.load_model("base")  # You can choose "tiny", "base", "small", "medium", or "large"
    
    # Create a list to store the results
    results = []
    
    # Supported audio file extensions
    audio_extensions = {'.wav', '.mp3', '.aac', '.m4a', '.flac', '.ogg', '.wma'}
    
    # Get all audio files in the folder
    audio_files = [
        f for f in os.listdir(input_folder)
        if os.path.splitext(f.lower())[1] in audio_extensions
    ]
    
    if not audio_files:
        print(f"No audio files found in {input_folder}")
        return results
    
    print(f"Found {len(audio_files)} audio file(s) to transcribe...")
    
    # Iterate through all audio files in the folder
    for idx, filename in enumerate(audio_files, 1):
        print(f"Transcribing {idx}/{len(audio_files)}: {filename}")
        
        # Full path to the audio file
        file_path = os.path.join(input_folder, filename)
        
        try:
            # Transcribe the audio file using Whisper
            result = model.transcribe(file_path)
            transcript = result["text"]
            
            # Extract information from the filename based on configured format
            # For Fabla files: format is PARTICIPANT_ID_DATE_TIME.extension
            # Example: P001_2024-01-15_14-30-00.wav
            participant_id, date, time = extract_filename_info(filename, filename_config)
            
            # Append the results
            results.append({
                'Filename': filename,
                'Participant ID': participant_id,
                'Date': date,
                'Time': time,
                'Transcript': transcript
            })
        except Exception as e:
            print(f"Error transcribing {filename}: {str(e)}")
            continue
    
    return results

def main():
    """Main function to orchestrate the transcription process."""
    # Prompt user to select a folder
    input_folder = select_folder()
    
    if not input_folder:
        print("No folder selected. Exiting.")
        return
    
    print(f"Selected folder: {input_folder}")
    
    # Get the original folder name
    original_folder_name = os.path.basename(input_folder.rstrip('/\\'))
    
    # Create output folder in Downloads
    downloads_folder = get_downloads_folder()
    output_folder_name = f"{original_folder_name}_transcripts"
    output_folder = downloads_folder / output_folder_name
    
    # Create the output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"Output folder: {output_folder}")
    
    # Get filename format configuration from user
    filename_config = get_filename_format_config()
    
    # Transcribe all audio files
    results = transcribe_audio_files(input_folder, output_folder, filename_config)
    
    if not results:
        print("No files were transcribed.")
        return
    
    # Create a DataFrame from the results
    df = pd.DataFrame(results)
    
    # Save the DataFrame to a CSV file
    output_file = output_folder / "transcripts.csv"
    df.to_csv(output_file, index=False)
    
    # Console output with summary
    print("\n" + "="*60)
    print(f"Transcription complete!")
    print(f"Files transcribed: {len(results)}")
    print(f"Output file: {output_file}")
    print("="*60)

if __name__ == "__main__":
    main()
