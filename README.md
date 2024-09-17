# Voice applications and emotion recognition

This project has the purpose to create some applications about voice tasks: recognition, translation, emotion detection and something more. I mostly use pre-trained models from transformer library and implement anything I can think of (guy, explainability, apps).

## Voice Translator

Questa applicazione permette di registrare audio in italiano e tradurlo in inglese utilizzando un'interfaccia grafica user-friendly.

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

Run `main.py`:

```
python main.py
```

1. Clicca su "Registra" per iniziare la registrazione audio.
2. Parla chiaramente in italiano.
3. Il testo riconosciuto apparirà nella casella di testo superiore.
4. Clicca su "Traduci" per ottenere la traduzione in inglese.

### Contributions

Pull request are really welcome. For important changes, open an issue firstly to discuss about what you would like to modify