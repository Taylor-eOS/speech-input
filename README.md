**A lightweight GUI tool for recording and transcribing speech to text on Linux using the built-in microphone**, designed to provide functionality similar to mobile device speech input tools.<br>
![t2](https://github.com/user-attachments/assets/4822348d-c006-498b-b0f2-806259a62020)<br>

This tool uses the `arecord` command for audio recording, which is compatible with most Linux systems and does not depend on specific hardware. It leverages Whisper's robust transcription capabilities, including support for multiple languages. 

**Features**:
- Simple recording controls integrated into the GUI.
- Foreign language transcription: Enter the desired language code (e.g., `en` for English) before recording.  
- Real-time status updates in the interface, so you know when to start speaking or when transcription is in progress. 

To achieve optimal transcription results, ensure you speak slowly and clearly, leaving slight pauses between words. Position yourself close to your computers microphone, and consider adjusting the microphone input volume—lower settings can sometimes improve clarity and reduce noise.  

**Instructions**:  
Install the dependencies listed in `requirements.txt` and run `record.py` to start the tool.
