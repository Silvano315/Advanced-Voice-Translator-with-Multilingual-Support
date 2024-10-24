# GUI Voice Translator from Italian speech

This project is a proof-of-concept for a Translator GUI: an application that, firstly, uses a speech to text model to capture Italian sentences and then, uses a translation model to obtain the same sentences in other five other languages. I mostly use pre-trained models from transformer library and implement anything I can think of (guy, explainability, apps).

## Voice Translator

This application allows you to record audio in Italian and translate it into English using a user-friendly graphical interface.

### Requirements

- Python 3.7+
- PyQt6
- SpeechRecognition
- transformers
- torch
- pydub

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/tuousername/VoiceTranslator.git
   ```

2. Go to projects directory:
   ```
   cd Voice-applications-and-emotion-recognition
   ```

3. Install packages:
   ```
   pip install -r requirements.txt
   ```

### Usage

Run `main_translator.py`:

```
python main_translator.py
```

1. Click on "Record" to start recording audio.
2. Speaks clearly in Italian.
3. The recognized text will appear in the upper text box.
4. Click on "Translate" to get the translation in English.

### Contributions

Pull request are really welcome. For important changes, open an issue firstly to discuss about what you would like to modify
