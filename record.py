import os
import subprocess
import threading
from tkinter import Tk, Button, Text, Entry, Label, END
import whisper
import tempfile

AUDIO_DIR = tempfile.gettempdir()
AUDIO_FILENAME = "recorded_audio.wav"
AUDIO_PATH = os.path.join(AUDIO_DIR, AUDIO_FILENAME)

MODEL_SIZE = "large"
whisper_model = whisper.load_model(MODEL_SIZE)
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
    transcription_box.insert(END, "Recording started. You can begin speaking now.\n")
    record_button.config(text="Stop Recording")

def stop_recording():
    global recording_process
    if recording_process:
        recording_process.terminate()
        recording_process = None
        transcription_box.delete(1.0, END)
        transcription_box.insert(END, "Transcription in progress...\n")
        threading.Thread(target=transcribe_audio).start()
        record_button.config(text="Start Recording")

def transcribe_audio():
    if not os.path.exists(AUDIO_PATH):
        return
    language_code = language_entry.get().strip() or "en"
    try:
        result = whisper_model.transcribe(AUDIO_PATH, language=language_code)
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

def select_all(event):
    transcription_box.tag_add("sel", "1.0", "end")
    return "break"

root = Tk()
root.title("Speech-to-Text Transcription Tool")

record_button = Button(root, text="Start Recording", command=toggle_recording, width=20)
record_button.grid(row=0, column=0, columnspan=2, pady=5)

language_label = Label(root, text="Language Code:")
language_label.grid(row=1, column=0, sticky="e", padx=5)
language_entry = Entry(root, width=5)
language_entry.grid(row=1, column=1, sticky="w", padx=5)
language_entry.insert(0, "en")

transcription_box = Text(root, wrap="word", height=15, width=50)
transcription_box.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
transcription_box.bind("<Control-a>", select_all)

root.mainloop()

