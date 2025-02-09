import os
import subprocess
import threading
from tkinter import Tk, Button, Text, END
import tempfile
import warnings
from transformers import pipeline

warnings.filterwarnings("ignore", category=FutureWarning)

AUDIO_DIR = tempfile.gettempdir()
AUDIO_FILENAME = "recording.wav"
AUDIO_PATH = os.path.join(AUDIO_DIR, AUDIO_FILENAME)

# Load the Whisper turbo model using the transformers pipeline
asr_model = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3-turbo")

recording_process = None

def toggle_recording():
    global recording_process
    if recording_process is None:
        start_recording()
    else:
        stop_recording()

def start_recording():
    global recording_process
    recording_process = subprocess.Popen(
        ["arecord", "-f", "cd", AUDIO_PATH],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    transcription_box.delete(1.0, END)
    transcription_box.insert(END, "Recording started.\n")
    record_button.config(text="Stop Recording")
    transcription_box.after(500, lambda: transcription_box.insert(END, "...\n"))

def stop_recording():
    global recording_process
    if recording_process:
        recording_process.terminate()
        recording_process = None
        transcription_box.delete(1.0, END)
        transcription_box.insert(END, "Transcription in progress...\n")
        record_button.config(state="disabled")  # Disable recording during transcription
        threading.Thread(target=transcribe_audio).start()

def transcribe_audio():
    if not os.path.exists(AUDIO_PATH):
        return
    try:
        result = asr_model(AUDIO_PATH)
        transcription = result['text'].strip()
        transcription_box.delete(1.0, END)
        transcription_box.insert(END, transcription)
    except Exception as e:
        print(f"Transcription error: {e}")
    finally:
        try:
            os.remove(AUDIO_PATH)
        except OSError as e:
            print(f"Error deleting audio file: {e}")
        record_button.config(state="normal", text="Start Recording")  # Re-enable recording button

def select_all(event):
    transcription_box.tag_add("sel", "1.0", "end")
    return "break"

root = Tk()
root.title("Speech-to-Text Transcription Tool")

record_button = Button(root, text="Start Recording", command=toggle_recording, width=20)
record_button.grid(row=0, column=0, columnspan=2, pady=5)

transcription_box = Text(root, wrap="word", height=15, width=50)
transcription_box.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
transcription_box.bind("<Control-a>", select_all)

root.mainloop()

