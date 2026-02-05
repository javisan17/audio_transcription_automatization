# src/gui/gui_app.py

"""Interactive graphical interface with Tkinter."""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from audio import load_audio, record_audio
from audio.recorder import AudioRecorder
from logger import get_logger
from output import copy_to_clipboard, save_to_txt
from transcription import transcribe_audio


logger = get_logger(__name__)


# Determine base path -works in both development and executable
if getattr(sys, "frozen", False):
    # Ejecutable compilado
    base_dir = os.path.dirname(sys.executable)
    project_root = base_dir
else:
    # In development
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    project_root = base_dir

# Add paths to import modules (make sure `src` is in sys.path)
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)


# Note: the logging/windowed setting to use console mode has been removed.


class AudioTranscriptionGUI:
    """Main class for the audio transcription graphical interface."""

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Audio Automation - Transcription")
        self.root.geometry("625x753")
        self.root.resizable(False, False)

        # Control variables
        self.is_recording = False
        self.recording_duration = tk.IntVar(value=30)
        self.transcription_text = ""
        self.audio_recorder = None
        self.recording_thread = None

        # Set styles
        self.setup_styles()

        # Create the interface
        self.create_widgets()

    def setup_styles(self):
        """Configure interface styles."""
        style = ttk.Style()
        style.theme_use("clam")

        # Custom colors
        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Heading.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Info.TLabel", font=("Helvetica", 10))

    def create_widgets(self):
        """Create the interface widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(
            main_frame, text="AUDIO AUTOMATION", style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Separator
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=5
        )

        # ===== SECTION 1: TRANSCRIBE FILE =====
        file_frame = ttk.LabelFrame(
            main_frame, text="Option 1: Transcribe File", padding="10"
        )
        file_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(
            file_frame, text="Select an audio file:", style="Info.TLabel"
        ).grid(row=0, column=0, sticky="w")

        self.file_path_var = tk.StringVar(value="No file selected")
        file_path_label = ttk.Label(
            file_frame, textvariable=self.file_path_var, foreground="gray"
        )
        file_path_label.grid(row=1, column=0, sticky="w", padx=(20, 0))

        ttk.Button(
            file_frame, text="Select File", command=self.select_file
        ).grid(row=2, column=0, sticky="ew", pady=(5, 0))
        ttk.Button(
            file_frame, text="Transcribe File", command=self.transcribe_file
        ).grid(row=3, column=0, sticky="ew", pady=5)

        # ===== SECTION 2: RECORD AND TRANSCRIBE =====
        record_frame = ttk.LabelFrame(
            main_frame, text="Option 2: Record and Transcribe", padding="10"
        )
        record_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(record_frame, text="Recording mode:", style="Info.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        # Recording options
        mode_frame = ttk.Frame(record_frame)
        mode_frame.grid(row=1, column=0, sticky="ew", pady=(5, 10))

        self.record_mode = tk.StringVar(value="duration")
        ttk.Radiobutton(
            mode_frame,
            text="Fixed duration (seconds):",
            variable=self.record_mode,
            value="duration",
            command=self._update_record_mode,
        ).pack(side="left")
        ttk.Radiobutton(
            mode_frame,
            text="Control manual (START/STOP)",
            variable=self.record_mode,
            value="manual",
            command=self._update_record_mode,
        ).pack(side="left", padx=20)

        # Frame for fixed duration
        self.duration_frame = ttk.Frame(record_frame)
        self.duration_frame.grid(row=2, column=0, sticky="w", pady=(5, 0))

        spinbox_frame = ttk.Frame(self.duration_frame)
        spinbox_frame.pack(side="left")

        ttk.Spinbox(
            spinbox_frame,
            from_=5,
            to=300,
            textvariable=self.recording_duration,
            width=5,
        ).pack(side="left")
        ttk.Label(spinbox_frame, text="seconds", style="Info.TLabel").pack(
            side="left", padx=5
        )

        # Buttons for fixed duration
        self.duration_button = ttk.Button(
            self.duration_frame, text="Record", command=self.start_recording_duration
        )
        self.duration_button.pack(side="left", padx=10)

        # Frame for manual control
        self.manual_frame = ttk.Frame(record_frame)
        self.manual_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))

        self.start_button = ttk.Button(
            self.manual_frame,
            text="Start Recording",
            command=self.start_recording_manual,
            style="Accent.TButton",
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(
            self.manual_frame,
            text="Stop Recording",
            command=self.stop_recording_manual,
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=5)

        # Recording status label
        self.recording_status_var = tk.StringVar(value="")
        ttk.Label(
            record_frame, textvariable=self.recording_status_var, foreground="blue"
        ).grid(row=3, column=0, sticky="w", padx=(20, 0))

        #Hide manual frame by default
        self.manual_frame.grid_remove()

        # ===== SECTION 3: TRANSCRIPT RESULT =====
        result_frame = ttk.LabelFrame(
            main_frame, text="Transcription Result", padding="10"
        )
        result_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)

        # Scrolling text
        self.result_text = scrolledtext.ScrolledText(
            result_frame, height=10, width=70, wrap=tk.WORD
        )
        self.result_text.grid(
            row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10)
        )
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        # Buttons for the result
        button_frame = ttk.Frame(result_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        ttk.Button(
            button_frame,
            text="Copy to clipboard",
            command=self.copy_to_clipboard,
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame, text="Save as file", command=self.save_to_file
        ).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🗑️ Clean", command=self.clear_text).pack(
            side="left", padx=5
        )

        # ===== SECTION 4: GENERAL BUTTONS =====
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Button(footer_frame, text="ℹ️ About", command=self.show_about).pack(
            side="left", padx=5
        )
        ttk.Button(footer_frame, text="❌ Exit", command=self.on_closing).pack(
            side="right", padx=5
        )

        # Configure row weight for responsiveness
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_file(self):
        """Select an audio file."""
        file_types = [
            ("Audio files", "*.wav *.mp3 *.m4a *.flac *.ogg *.mp4"),
            ("All files", "*.*"),
        ]

        file_path = filedialog.askopenfilename(
            title="Select an audio file", filetypes=file_types
        )

        if file_path:
            self.file_path_var.set(os.path.basename(file_path))
            self.selected_file = file_path

    def transcribe_file(self):
        """Transcribe a selected audio file."""
        if not hasattr(self, "selected_file"):
            messagebox.showwarning(
                "Warning", "Please select a file first."
            )
            return

        if not os.path.isfile(self.selected_file):
            messagebox.showerror("Error", "The file does not exist.")
            return

        # Run in a separate thread so as not to block the interface
        thread = threading.Thread(target=self._transcribe_file_thread, daemon=True)
        thread.start()

    def _transcribe_file_thread(self):
        """Thread to transcribe file without blocking the GUI."""
        try:
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)

            # Check if it is MP4
            if self.selected_file.lower().endswith(".mp4"):
                self.result_text.insert(
                    tk.END, "Detected MP4 file, converting to WAV...\n"
                )
            else:
                self.result_text.insert(tk.END, "Loading audio file...\n")

            self.result_text.update()

            # Load audio (this will convert MP4 if necessary)
            audio_preparado = load_audio(self.selected_file)

            self.result_text.insert(tk.END, "Transcribing...\n")
            self.result_text.update()

            # Transcribe
            self.transcription_text = transcribe_audio(audio_preparado)

            if self.transcription_text:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, self.transcription_text)
                messagebox.showinfo("Success", "Transcription completed")
            else:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(
                    tk.END,
                    "No transcription was generated." \
                    " Verify that the file contains valid audio.",
                )
                messagebox.showerror("Error", "No transcription was generated.")

        except Exception as e:
            error_msg = f"Error during transcription:\n{str(e)}"
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, error_msg)
            messagebox.showerror("Error", error_msg)
            from logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Transcription error: {e}")
        finally:
            self.result_text.config(state="normal")

    def start_recording(self):
        """Start audio recording."""
        duration = self.recording_duration.get()

        if duration < 5 or duration > 300:
            messagebox.showwarning(
                "Warning", "The duration must be between 5 and 300 seconds."
            )
            return

        # Run in a separate thread
        thread = threading.Thread(
            target=self._recording_thread, args=(duration,), daemon=True
        )
        thread.start()

    def _recording_thread(self, duration):
        """Thread to record without blocking the GUI."""
        try:
            self.is_recording = True
            self.recording_status_var.set(f"Recording... ({duration}s)")
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(
                tk.END, f"Recording {duration} seconds of audio...\n"
            )
            self.result_text.update()

            # Grabar
            audio_grabado = record_audio(duration=duration)

            if not audio_grabado:
                messagebox.showerror("Error", "Error during recording.")
                self.recording_status_var.set("")
                self.duration_button.config(state="normal")
                return

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Transcribing recorded audio...\n")
            self.result_text.update()

            # Transcribe
            try:
                self.transcription_text = transcribe_audio(audio_grabado)

                if self.transcription_text:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, self.transcription_text)
                    messagebox.showinfo(
                        "Success", "Recording and transcription completed"
                    )
                else:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(
                        tk.END,
                        "The recorded audio could not be transcribed." \
                        "Make sure you have spoken clearly.",
                    )
                    messagebox.showerror(
                        "Error",
                        "No transcription could be obtained from the recorded audio.",
                    )
            except Exception as trans_error:
                error_msg = f"Error during transcription:\n{str(trans_error)}"
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, error_msg)
                messagebox.showerror("Transcription Error", error_msg)
                logger.exception(f"Transcription error: {trans_error}")

            self.recording_status_var.set("")

        except Exception as e:
            error_msg = f"Error during recording:\n{str(e)}"
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, error_msg)
            messagebox.showerror("Error", error_msg)
            logger.exception(f"Error during recording: {e}")
            self.recording_status_var.set("")
        finally:
            self.is_recording = False
            self.result_text.config(state="normal")
            self.duration_button.config(state="normal")

    def copy_to_clipboard(self):
        """Copy the transcribed text to the clipboard."""
        text = self.result_text.get(1.0, tk.END).strip()

        if not text:
            messagebox.showwarning("Warning", "There is no text to copy.")
            return

        try:
            copy_to_clipboard(text)
            messagebox.showinfo("Success", "Text copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Error copying text: {str(e)}")

    def save_to_file(self):
        """Save the transcribed text to a file."""
        text = self.result_text.get(1.0, tk.END).strip()

        if not text:
            messagebox.showwarning("Warning", "There is no text to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if file_path:
            try:
                save_to_txt(text, file_path)
                messagebox.showinfo("Success", f"✅ File saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")

    def clear_text(self):
        """Clear the text area."""
        self.result_text.delete(1.0, tk.END)
        self.transcription_text = ""

    def show_about(self):
        """Show information about the application."""
        about_text = """
Audio Automation -Transcription

Version: 2.0
Description: Application to transcribe audio files
or record and transcribe in real time using Whisper AI.

Features:
• Transcribe audio files (.wav, .mp3, .m4a, .flac, .ogg)
• Record audio with fixed duration
• Record audio with manual control (START/STOP)
• Copy transcripts to clipboard
• Save transcripts to .txt files

Technologies:
• OpenAI Whisper (transcript)
• Tkinter (graphical interface)
• SoundDevice (recording)
• SoundFile (audio processing)
        """
        messagebox.showinfo("About", about_text)

    def _update_record_mode(self):
        """Update frame visibility according to the selected mode."""
        if self.record_mode.get() == "duration":
            self.duration_frame.grid()
            self.manual_frame.grid_remove()
        else:
            self.duration_frame.grid_remove()
            self.manual_frame.grid()

    def start_recording_duration(self):
        """Start audio recording with fixed duration."""
        duration = self.recording_duration.get()

        if duration < 5 or duration > 300:
            messagebox.showwarning(
                "Warning", "The duration must be between 5 and 300 seconds."
            )
            return

        self.duration_button.config(state="disabled")

        # Run in a separate thread (NOT daemon so it terminates completely)
        thread = threading.Thread(
            target=self._recording_thread, args=(duration,), daemon=False
        )
        thread.start()

    def _recording_thread(self, duration):
        """Thread to record without blocking the GUI."""
        try:
            self.is_recording = True
            self.recording_status_var.set(f"Recording... ({duration}s)")
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(
                tk.END, f"Recording {duration} seconds of audio...\n"
            )
            self.result_text.update()

            # Grabar
            audio_grabado = record_audio(duration=duration)

            if not audio_grabado:
                messagebox.showerror("Error", "Error during recording.")
                self.recording_status_var.set("")
                self.duration_button.config(state="normal")
                return

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Transcribing recorded audio...\n")
            self.result_text.update()

            # Transcribe
            try:
                self.transcription_text = transcribe_audio(audio_grabado)

                if self.transcription_text:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, self.transcription_text)
                    messagebox.showinfo(
                        "Success", "Recording and transcription completed"
                    )
                else:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(
                        tk.END,
                        "No transcription of the recorded audio could be obtained. " \
                        "Ensure you spoke clearly.",
                    )
                    messagebox.showerror(
                        "Error",
                        "No transcription of the recorded audio could be obtained.",
                    )
            except Exception as trans_error:
                error_msg = f"Error when transcribing:\n{str(trans_error)}"
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, error_msg)
                messagebox.showerror("Transcription Error", error_msg)
                logger.exception(f"Error in transcription: {trans_error}")

            self.recording_status_var.set("")

        except Exception as e:
            error_msg = f"Error during recording:\n{str(e)}"
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, error_msg)
            messagebox.showerror("Error", error_msg)
            logger.exception(f"Error during recording: {e}")
            self.recording_status_var.set("")
        finally:
            self.is_recording = False
            self.result_text.config(state="normal")
            self.duration_button.config(state="normal")

    def start_recording_manual(self):
        """Start manual recording (no time limit)."""
        self.audio_recorder = AudioRecorder()
        self.audio_recorder.start_recording()

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.recording_status_var.set(
            "Recording... (press STOP to finish)"
        )

        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(
            tk.END,
            "Recording audio in real time...\n"
            "Press 'Stop Recording' when finished.\n",
        )
        self.result_text.update()

    def stop_recording_manual(self):
        """Stop manual recording and transcribe."""
        if not self.audio_recorder:
            messagebox.showerror("Error", "No active recording.")
            return

        self.stop_button.config(state="disabled")
        self.start_button.config(state="normal")
        self.recording_status_var.set("Processing recorded audio...")

        # Stop recording
        audio_grabado = self.audio_recorder.stop_recording()
        self.audio_recorder = None

        if not audio_grabado:
            messagebox.showerror(
                "Error", "Error during recording. No audio was captured."
            )
            self.recording_status_var.set("")
            return

        #Transcribe to a separate thread (NOT daemon so it terminates completely)
        thread = threading.Thread(
            target=self._transcribe_manual_recording,
            args=(audio_grabado,),
            daemon=False,
        )
        thread.start()

    def _transcribe_manual_recording(self, audio_path):
        """Transcribe recorded audio manually."""
        try:
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Transcribing recorded audio...\n")
            self.result_text.update()

            # Transcribe
            try:
                self.transcription_text = transcribe_audio(audio_path)

                if self.transcription_text:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, self.transcription_text)
                    messagebox.showinfo(
                        "Success", "Recording and transcription completed"
                    )
                else:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(
                        tk.END,
                        "The recorded audio could not be transcribed." \
                        "Make sure you have spoken clearly.",
                    )
                    messagebox.showerror(
                        "Error",
                        "Could not obtain transcription of the recorded audio.",
                    )
            except Exception as trans_error:
                error_msg = f"Error transcribing audio:\n{str(trans_error)}"
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, error_msg)
                messagebox.showerror("Transcription Error", error_msg)
                logger.exception(f"Error in transcription: {trans_error}")

            self.recording_status_var.set("")

        except Exception as e:
            error_msg = f"Error during recording:\n{str(e)}"
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, error_msg)
            messagebox.showerror("Error", error_msg)
            logger.exception(f"Error in recording: {e}")
            self.recording_status_var.set("")
        finally:
            self.result_text.config(state="normal")

    # def start_recording(self):
    #     """Iniciar grabación de audio
    #        (DEPRECATED - se mantiene para compatibilidad)."""
    #     duration = self.recording_duration.get()

    #     if duration < 5 or duration > 300:
    #         messagebox.showwarning(
    #             "Advertencia", "La duración debe estar entre 5 y 300 segundos."
    #         )
    #         return

    #     # Ejecutar en un hilo separado
    #     thread = threading.Thread(
    #         target=self._recording_thread, args=(duration,), daemon=True
    #     )
    #     thread.start()

    def on_closing(self):
        """Handle application closure."""
        # Stop any recording in progress
        if (
            hasattr(self, "audio_recorder")
            and self.audio_recorder
            and self.audio_recorder.is_recording
        ):
            self.audio_recorder.is_recording = False
            if self.audio_recorder.thread:
                self.audio_recorder.thread.join(timeout=1)

        # Close the application
        self.root.quit()
        self.root.destroy()


def main():
    """Start the GUI."""
    root = tk.Tk()
    AudioTranscriptionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()