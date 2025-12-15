import os
import whisper
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import threading
import sys
import subprocess

# Try to import tkinterdnd2 for drag & drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fabla Whisper Transcription Tool")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        # Set application background color
        self.root.configure(bg="#4186F5")
        self.icon_image = None  # Hold reference to original icon
        self.icon_image_small = None  # Scaled icon for UI
        self.load_icon()
        
        # Variables
        self.selected_folder = None
        self.filename_config = {
            'delimiter': '_',
            'id_position': 0,
            'date_position': 1,
            'time_position': 2
        }
        self.is_processing = False
        
        # Setup UI
        self.setup_ui()
        
        # Check for FFmpeg
        self.check_ffmpeg()
        
        # Try to enable drag & drop (if tkinterdnd2 is available)
        self.setup_drag_drop()
    
    def setup_ui(self):
        # Palette (inspired by app screenshot)
        main_bg = "#5C86FF"       # base blue background
        card_bg = "#FFFFFF"       # white cards
        text_dark = "#1C2B3A"     # primary text
        text_muted = "#3F5870"    # secondary text
        accent = "#1C6BFF"        # accent blue for buttons/links
        text_light = "#FFFFFF"    # white text on blue

        # Configure styles to match background
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background=main_bg)
        style.configure("Main.TLabel", background=main_bg, foreground=text_light)
        style.configure("Title.TLabel", background=main_bg, foreground=text_light, font=("Helvetica", 20, "bold"))

        # Card-like sections (simulate rounded cards with padding and flat borders)
        style.configure(
            "Card.TLabelframe",
            background=card_bg,
            borderwidth=0,
            relief="flat",
            labelmargins=(10, 6, 10, 0),
            padding=(16, 14, 16, 16),
        )
        style.configure(
            "Card.TLabelframe.Label",
            background=card_bg,
            foreground=text_dark,
            padding=(2, 0),
            font=("Helvetica", 11, "bold"),
        )
        style.configure("Card.TFrame", background=card_bg)
        style.configure("Card.TLabel", background=card_bg, foreground=text_dark)

        # Inputs
        style.configure("Custom.TEntry",
                        fieldbackground=card_bg,
                        foreground=text_dark,
                        bordercolor="#D0D7E2",
                        lightcolor="#D0D7E2",
                        darkcolor="#D0D7E2")
        style.configure("Custom.TCombobox",
                        fieldbackground=card_bg,
                        foreground=text_dark,
                        background=card_bg,
                        bordercolor="#D0D7E2",
                        lightcolor="#D0D7E2",
                        darkcolor="#D0D7E2")

        # Buttons
        style.configure("Section.TButton",
                        background=card_bg,
                        foreground=accent,
                        borderwidth=1)
        style.map("Section.TButton",
                  foreground=[("disabled", "#8ca7e0")],
                  background=[("active", "#f2f6ff"),
                              ("disabled", "#eef2fb")])

        # Main container
        main_frame = ttk.Frame(self.root, padding="20", style="Main.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Fabla Whisper Transcription",
            font=("Arial", 18, "bold"),
            image=self.icon_image_small if self.icon_image_small else None,
            compound=tk.LEFT,
            padding=(6, 0),
            style="Title.TLabel",
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Instructions
        instructions = ttk.Label(
            main_frame,
            text="Drag & drop a folder with audio files here, or click 'Select Folder' to browse.",
            font=("Arial", 11),
            wraplength=780,
            justify=tk.CENTER,
            style="Main.TLabel",
        )
        instructions.grid(row=1, column=0, pady=(0, 10))

        # Top section holding folder selection and filename format side-by-side
        top_frame = ttk.Frame(main_frame, style="Main.TFrame")
        top_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        
        # Drag & drop area (card)
        self.drop_frame = ttk.LabelFrame(top_frame, text="Drop Folder Here", padding="15", style="Card.TLabelframe")
        self.drop_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 8))
        self.drop_frame.columnconfigure(0, weight=1)
        
        self.drop_label = ttk.Label(self.drop_frame, 
                                    text="📁 No folder selected",
                                    font=("Arial", 12),
                                    style="Card.TLabel")
        self.drop_label.grid(row=0, column=0, pady=6)
        
        # Select folder button
        select_btn = ttk.Button(self.drop_frame, text="Select Folder", 
                               command=self.select_folder_dialog,
                               style="Section.TButton")
        select_btn.grid(row=1, column=0, pady=6)

        # File type indicator inside drop area
        self.filetype_label = ttk.Label(
            self.drop_frame,
            text="File types: .wav, .mp3, .aac",
            font=("Arial", 10),
            style="Card.TLabel"
        )
        self.filetype_label.grid(row=2, column=0, pady=(4, 0))
        
        # Filename format configuration
        config_frame = ttk.LabelFrame(top_frame, text="Filename Format (Optional)", padding="12", style="Card.TLabelframe")
        config_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 0))
        config_frame.columnconfigure(1, weight=1)
        
        ttk.Label(config_frame, text="Delimiter:", style="Card.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.delimiter_var = tk.StringVar(value="_")
        delimiter_entry = ttk.Entry(config_frame, textvariable=self.delimiter_var, width=10, style="Custom.TEntry")
        delimiter_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(config_frame, text="ID Position:", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.id_pos_var = tk.StringVar(value="0")
        id_pos_entry = ttk.Entry(config_frame, textvariable=self.id_pos_var, width=10, style="Custom.TEntry")
        id_pos_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(config_frame, text="Date Position:", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.date_pos_var = tk.StringVar(value="1")
        date_pos_entry = ttk.Entry(config_frame, textvariable=self.date_pos_var, width=10, style="Custom.TEntry")
        date_pos_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(config_frame, text="Time Position:", style="Card.TLabel").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.time_pos_var = tk.StringVar(value="2")
        time_pos_entry = ttk.Entry(config_frame, textvariable=self.time_pos_var, width=10, style="Custom.TEntry")
        time_pos_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        help_text = ttk.Label(config_frame, 
                             text="Example: P001_2024-01-15_14-30-00.wav\n(Default settings work for this format)",
                             font=("Arial", 9),
                             style="Card.TLabel")
        help_text.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        # File type filter
        ttk.Label(config_frame, text="File type:", style="Card.TLabel").grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 5))
        self.filetype_var = tk.StringVar(value="All (.wav, .mp3, .aac)")
        filetype_combo = ttk.Combobox(
            config_frame,
            text="File type",
            textvariable=self.filetype_var,
            state="readonly",
            values=[
                "All (.wav, .mp3, .aac)",
                ".wav only",
                ".mp3 only",
                ".aac only",
            ],
            width=18,
            style="Custom.TCombobox",
        )
        filetype_combo.grid(row=5, column=1, sticky=tk.W, pady=(10, 5))
        filetype_combo.bind("<<ComboboxSelected>>", lambda e: self.update_filetype_label())
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="12", style="Card.TLabelframe")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(progress_frame, text="Ready", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_text = scrolledtext.ScrolledText(
            progress_frame,
            height=8,
            width=60,
            background=card_bg,
            foreground=text_dark,
            insertbackground=text_dark,
            borderwidth=1,
            relief="flat",
        )
        self.progress_text.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Transcribe button (bigger, with icon)
        self.transcribe_btn = ttk.Button(
            main_frame,
            text="🎧  Start Transcription",
            command=self.start_transcription,
            state=tk.DISABLED,
            width=28,
            padding=(10, 12),
        )
        self.transcribe_btn.grid(row=4, column=0, pady=24)
        
        # Configure grid weights
        main_frame.rowconfigure(3, weight=1)
        progress_frame.rowconfigure(2, weight=1)
    
    def check_ffmpeg(self):
        """Check if FFmpeg is installed and accessible."""
        try:
            # Try to run ffmpeg -version
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, 
                                  timeout=2)
            if result.returncode == 0:
                self.log_message("✓ FFmpeg detected - audio processing ready")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        
        # FFmpeg not found
        self.log_message("⚠ WARNING: FFmpeg not found!")
        self.log_message("FFmpeg is required for processing audio files.")
        self.log_message("Installation instructions:")
        if sys.platform == "darwin":
            self.log_message("  macOS: brew install ffmpeg")
        elif sys.platform == "win32":
            self.log_message("  Windows: Download from https://ffmpeg.org/download.html")
        else:
            self.log_message("  Linux: sudo apt install ffmpeg")
        self.log_message("")
        return False
    
    def setup_drag_drop(self):
        """Setup drag & drop if tkinterdnd2 is available."""
        if DND_AVAILABLE:
            try:
                # Enable drag & drop on the drop frame
                self.drop_frame.drop_target_register(DND_FILES)
                self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
                self.log_message("Drag & drop enabled! You can drag folders directly onto the drop area.")
            except Exception as e:
                self.log_message(f"Note: Drag & drop setup failed: {e}. Using folder selection button instead.")
        else:
            self.log_message("Note: Install 'tkinterdnd2' for drag & drop support. Using folder selection button instead.")
    
    def load_icon(self):
        """Load window/icon image if available."""
        try:
            icon_path = Path(__file__).parent / "fabla-ghost.png"
            if icon_path.exists():
                self.icon_image = tk.PhotoImage(file=str(icon_path))
                # Make a smaller version for UI (roughly 4x smaller)
                self.icon_image_small = self.icon_image.subsample(4, 4)
                # Use the small icon for window icon and labels
                self.root.iconphoto(False, self.icon_image_small)
        except Exception:
            # Silently ignore icon issues
                self.icon_image = None
                self.icon_image_small = None

    def on_drop(self, event):
        """Handle drag & drop event."""
        if self.is_processing:
            messagebox.showwarning("Processing", "Please wait for current transcription to finish.")
            return
        
        # Get dropped path
        dropped_path = event.data.strip('{}')
        
        # Check if it's a folder
        if os.path.isdir(dropped_path):
            self.set_selected_folder(dropped_path)
        else:
            # If it's a file, use its parent directory
            parent_dir = os.path.dirname(dropped_path)
            if os.path.isdir(parent_dir):
                self.set_selected_folder(parent_dir)
            else:
                messagebox.showerror("Error", "Please drop a folder, not a file.")
    
    def select_folder_dialog(self):
        """Open folder selection dialog."""
        if self.is_processing:
            messagebox.showwarning("Processing", "Please wait for current transcription to finish.")
            return
        
        folder = filedialog.askdirectory(title="Select folder containing audio files")
        if folder:
            self.set_selected_folder(folder)
    
    def set_selected_folder(self, folder_path):
        """Set the selected folder and update UI."""
        self.selected_folder = folder_path
        folder_name = os.path.basename(folder_path.rstrip('/\\'))
        self.drop_label.config(text=f"📁 {folder_name}", foreground="green")
        self.transcribe_btn.config(state=tk.NORMAL)
        self.log_message(f"Selected folder: {folder_path}")
        
        # Count audio files (respecting selected file type filter)
        selected_exts = self.get_selected_extensions()
        audio_files = [
            f for f in os.listdir(folder_path)
            if os.path.splitext(f.lower())[1] in selected_exts
        ]
        self.log_message(
            f"Found {len(audio_files)} audio file(s) in folder "
            f"matching {', '.join(sorted(selected_exts))}"
        )
        self.update_filetype_label()
    
    def get_filename_config(self):
        """Get filename configuration from UI."""
        try:
            return {
                'delimiter': self.delimiter_var.get() or '_',
                'id_position': int(self.id_pos_var.get()) if self.id_pos_var.get().isdigit() else 0,
                'date_position': int(self.date_pos_var.get()) if self.date_pos_var.get().isdigit() else 1,
                'time_position': int(self.time_pos_var.get()) if self.time_pos_var.get().isdigit() else 2
            }
        except:
            return self.filename_config

    def get_selected_extensions(self):
        """
        Return a set of file extensions to include based on the user's selection.

        Only .wav, .mp3, and .aac are considered, as requested.
        """
        mapping = {
            "All (.wav, .mp3, .aac)": {".wav", ".mp3", ".aac"},
            ".wav only": {".wav"},
            ".mp3 only": {".mp3"},
            ".aac only": {".aac"},
        }
        return mapping.get(self.filetype_var.get(), {".wav", ".mp3", ".aac"})

    def update_filetype_label(self):
        """Update the drop area indicator with the selected file types."""
        exts = sorted(self.get_selected_extensions())
        self.filetype_label.config(text=f"File types: {', '.join(exts)}")
    
    def extract_filename_info(self, filename, config):
        """Extract participant ID, date, and time from filename."""
        name_without_ext = os.path.splitext(filename)[0]
        parts = name_without_ext.split(config['delimiter'])
        
        participant_id = parts[config['id_position']] if len(parts) > config['id_position'] else ""
        date = parts[config['date_position']] if len(parts) > config['date_position'] else ""
        time = parts[config['time_position']] if len(parts) > config['time_position'] else ""
        
        return participant_id, date, time
    
    def log_message(self, message):
        """Add message to progress text area."""
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_transcription(self):
        """Start transcription in a separate thread."""
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        
        if self.is_processing:
            return
        
        # Disable button and set processing flag
        self.is_processing = True
        self.transcribe_btn.config(state=tk.DISABLED)
        self.progress_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
        # Start transcription in background thread
        thread = threading.Thread(target=self.transcribe_files, daemon=True)
        thread.start()
    
    def transcribe_files(self):
        """Transcribe audio files (runs in background thread)."""
        try:
            self.log_message("Loading Whisper model...")
            self.status_label.config(text="Loading model...")
            self.root.update_idletasks()
            
            model = whisper.load_model("base")
            
            self.log_message("Model loaded successfully!")
            self.status_label.config(text="Transcribing...")
            
            # Get filename config
            filename_config = self.get_filename_config()
            
            # Get audio files, filtered by selected file type
            selected_exts = self.get_selected_extensions()
            audio_files = [
                f for f in os.listdir(self.selected_folder)
                if os.path.splitext(f.lower())[1] in selected_exts
            ]
            
            if not audio_files:
                self.log_message("No audio files found in selected folder.")
                self.status_label.config(text="No audio files found")
                self.is_processing = False
                self.transcribe_btn.config(state=tk.NORMAL)
                return
            
            self.log_message(f"Found {len(audio_files)} audio file(s) to transcribe")
            
            results = []
            
            # Transcribe each file
            for idx, filename in enumerate(audio_files, 1):
                self.log_message(f"Transcribing {idx}/{len(audio_files)}: {filename}")
                self.progress_var.set((idx - 1) / len(audio_files) * 100)
                self.root.update_idletasks()
                
                file_path = os.path.join(self.selected_folder, filename)
                
                try:
                    result = model.transcribe(file_path)
                    transcript = result["text"]
                    
                    participant_id, date, time = self.extract_filename_info(filename, filename_config)
                    
                    results.append({
                        'Filename': filename,
                        'Participant ID': participant_id,
                        'Date': date,
                        'Time': time,
                        'Transcript': transcript
                    })
                    
                    self.log_message(f"✓ Completed: {filename}")
                except Exception as e:
                    self.log_message(f"✗ Error transcribing {filename}: {str(e)}")
                    continue
            
            # Save results
            if results:
                self.log_message("\nSaving results to CSV...")
                self.status_label.config(text="Saving results...")
                
                # Save transcripts in the selected folder (no extra folder)
                output_folder = Path(self.selected_folder)
                df = pd.DataFrame(results)
                output_file = output_folder / "transcripts.csv"
                df.to_csv(output_file, index=False)
                
                self.progress_var.set(100)
                self.status_label.config(text="Complete!")
                
                self.log_message("\n" + "="*60)
                self.log_message("Transcription complete!")
                self.log_message(f"Files transcribed: {len(results)}")
                self.log_message(f"Output file: {output_file}")
                self.log_message("="*60)
                
                messagebox.showinfo("Success", 
                                  f"Transcription complete!\n\n"
                                  f"Files transcribed: {len(results)}\n"
                                  f"Output saved to:\n{output_file}")
            else:
                self.log_message("No files were successfully transcribed.")
                self.status_label.config(text="No files transcribed")
                messagebox.showwarning("Warning", "No files were successfully transcribed.")
            
        except Exception as e:
            error_msg = str(e)
            self.log_message(f"Error: {error_msg}")
            self.status_label.config(text="Error occurred")
            
            # Check if error is related to FFmpeg
            if "ffmpeg" in error_msg.lower() or "No such file" in error_msg or "not found" in error_msg.lower():
                error_dialog = f"FFmpeg Error\n\n{error_msg}\n\nFFmpeg is required to process audio files.\n\n"
                if sys.platform == "darwin":
                    error_dialog += "Install with: brew install ffmpeg"
                elif sys.platform == "win32":
                    error_dialog += "Download from: https://ffmpeg.org/download.html"
                else:
                    error_dialog += "Install with: sudo apt install ffmpeg"
                messagebox.showerror("FFmpeg Required", error_dialog)
            else:
                messagebox.showerror("Error", f"An error occurred:\n{error_msg}")
        finally:
            self.is_processing = False
            self.transcribe_btn.config(state=tk.NORMAL)

def main():
    # Set up error logging to file for debugging
    import traceback
    import logging
    from datetime import datetime
    
    log_file = Path.home() / "Downloads" / f"fabla-whisper-error-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    logging.basicConfig(
        filename=str(log_file),
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logging.error(f"Uncaught exception: {error_msg}")
        
        # Also try to show in a message box if possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"An error occurred. Check the log file:\n{log_file}")
            root.destroy()
        except:
            pass
    
    sys.excepthook = handle_exception
    
    try:
        # Use TkinterDnD root if available, otherwise use regular tk.Tk
        if DND_AVAILABLE:
            root = TkinterDnD.Tk()
        else:
            root = tk.Tk()
        
        app = TranscriptionApp(root)
        root.mainloop()
    except Exception as e:
        error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        logging.error(f"Failed to start application: {error_msg}")
        # Try to show error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}\n\nCheck log: {log_file}")
            root.destroy()
        except:
            print(f"Error: {e}\nCheck log: {log_file}")

if __name__ == "__main__":
    main()

