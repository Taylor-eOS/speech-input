import os
import subprocess
import threading
from tkinter import Tk, Button, Text, END
import whisper
import tempfile

# Paths and configurations
AUDIO_DIR = tempfile.gettempdir()
AUDIO_FILENAME = "recorded_audio.wav"
AUDIO_PATH = os.path.join(AUDIO_DIR, AUDIO_FILENAME)

# Load Whisper model
MODEL_SIZE = "small"
whisper_model = whisper.load_model(MODEL_SIZE)

# Function to start recording
def start_recording():
    global recording_process
    recording_process = subprocess.Popen(
    ["arecord", "-f", "cd", AUDIO_PATH],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    )
    log_to_console("Recording started...")

# Function to stop recording and transcribe
def stop_recording():
    global recording_process
    if recording_process:
        recording_process.terminate()
        recording_process = None
        log_to_console(f"Recording stopped. File saved at: {AUDIO_PATH}")
        threading.Thread(target=transcribe_audio).start()

# Function to transcribe audio
def transcribe_audio():
    if not os.path.exists(AUDIO_PATH):
        print("No audio file found. Please record first.")
        return

    try:
        result = whisper_model.transcribe(AUDIO_PATH)
        transcription = result['text'].strip()  # Remove trailing spaces
        transcription_box.delete(1.0, END)
        transcription_box.insert(END, transcription)
    except Exception as e:
        print(f"Transcription error: {e}")
    finally:
        try:
            os.remove(AUDIO_PATH)
            log_to_console("Temporary audio file deleted.")
        except OSError as e:
            print(f"Error deleting audio file: {e}")

# Helper function to log to the console
def log_to_console(message):
    print(message)

# Main GUI
root = Tk()
root.title("Speech-to-Text Transcription Tool")

# Buttons
record_button = Button(root, text="Start Recording", command=start_recording, width=20)
record_button.pack(pady=5)

stop_button = Button(root, text="Stop Recording", command=stop_recording, width=20)
stop_button.pack(pady=5)

# Text box for transcription results
transcription_box = Text(root, wrap="word", height=15, width=50)
transcription_box.pack(pady=10)

# Run the GUI
root.mainloop()

