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
asr_model = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3-turbo")
recording_process = None
segment_counter = 0
next_segment_to_show = 0
completed_segments = {}
order_lock = threading.Lock()
recording_timer = None

def begin_recording():
    global recording_process, recording_timer
    recording_process = subprocess.Popen(
        ["arecord", "-f", "cd", AUDIO_PATH],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    record_button.config(text="Stop recording")
    sendoff_button.config(state="normal")
    recording_timer = threading.Timer(29, send_off_segment)
    recording_timer.start()

def toggle_recording():
    global recording_process
    if recording_process is None:
        transcription_box.delete(1.0, END)
        begin_recording()
    else:
        finalize_recording()

def send_off_segment():
    global recording_process, segment_counter, recording_timer
    if recording_timer is not None:
        recording_timer.cancel()
        recording_timer = None
    if recording_process is None:
        return
    recording_process.terminate()
    try:
        recording_process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        recording_process.kill()
        recording_process.wait()
    segment_filename = os.path.join(AUDIO_DIR, f"segment_{segment_counter}.wav")
    try:
        os.rename(AUDIO_PATH, segment_filename)
    except OSError as e:
        print(f"Rename error: {e}")
        return
    current_segment = segment_counter
    segment_counter += 1
    threading.Thread(target=transcribe_segment, args=(segment_filename, current_segment)).start()
    begin_recording()

def finalize_recording():
    global recording_process, segment_counter, recording_timer
    if recording_timer is not None:
        recording_timer.cancel()
        recording_timer = None
    if recording_process is None:
        return
    recording_process.terminate()
    try:
        recording_process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        recording_process.kill()
        recording_process.wait()
    segment_filename = os.path.join(AUDIO_DIR, f"segment_{segment_counter}.wav")
    try:
        os.rename(AUDIO_PATH, segment_filename)
    except OSError as e:
        print(f"Rename error: {e}")
    current_segment = segment_counter
    segment_counter += 1
    threading.Thread(target=transcribe_segment, args=(segment_filename, current_segment)).start()
    recording_process = None
    record_button.config(text="Start recording")
    sendoff_button.config(state="disabled")

def transcribe_segment(segment_file, segment_id):
    if not os.path.exists(segment_file):
        return
    try:
        result = asr_model(segment_file)
        transcription = result['text'].strip()
        if transcription and transcription[-1] not in ".!?":
            transcription += "."
    except Exception as e:
        transcription = f"[Transcription error: {e}]"
    finally:
        try:
            os.remove(segment_file)
        except OSError as e:
            print(f"Delete error: {e}")
    with order_lock:
        global next_segment_to_show
        completed_segments[segment_id] = transcription
        while next_segment_to_show in completed_segments:
            transcription_box.insert(END, completed_segments[next_segment_to_show] + " ")
            transcription_box.see(END)
            del completed_segments[next_segment_to_show]
            next_segment_to_show += 1
        root.clipboard_clear()
        root.clipboard_append(transcription_box.get("1.0", "end-1c"))

root = Tk()
root.title("Speech-to-Text Transcription")
record_button = Button(root, text="Start recording", command=toggle_recording, width=18)
record_button.grid(row=0, column=0, pady=3, padx=0, sticky="e")
sendoff_button = Button(root, text="Send off segment", command=send_off_segment, width=18, state="disabled")
sendoff_button.grid(row=0, column=1, pady=3, padx=0, sticky="w")
transcription_box = Text(root, wrap="word", height=15, width=50)
transcription_box.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
def select_all(event):
    event.widget.tag_add("sel", "1.0", "end")
    return "break"
transcription_box.bind("<Control-a>", select_all)
def on_closing():
    finalize_recording()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
