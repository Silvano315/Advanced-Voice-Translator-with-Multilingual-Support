from PyQt6.QtCore import QThread, pyqtSignal
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import io
import wave
import numpy as np
from typing import Dict, Optional


class AudioThread(QThread):
    """
    A QThread subclass that handles real-time audio recording and speech recognition.
    Supports multiple languages and emits signals for detected text and audio data.
    """
    textDetected = pyqtSignal(str)
    audioDataReady = pyqtSignal(np.ndarray)
    
    def __init__(self, parent: Optional[QThread] = None, language: str = 'it-IT') -> None:
        """
        Initialize the audio thread with specified language settings.

        Args:
            parent: Parent QThread object (default: None)
            language: Language code for speech recognition (default: 'it-IT')
        """

        super().__init__(parent)
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        self.language = language
        
        self.supported_languages = {
            'italian': 'it-IT',
            'english': 'en-US',
            'spanish': 'es-ES',
            'french': 'fr-FR',
            'german': 'de-DE'
        }
    
    def set_language(self, language: str) -> None:
        """
        Set the recognition language if supported.

        Args:
            language: Language name in English (e.g., 'italian', 'english')

        Raises:
            ValueError: If the language is not supported
        """

        if language.lower() in self.supported_languages:
            self.language = self.supported_languages[language.lower()]
        else:
            raise ValueError(f"Language not supported: {language}")
    
    def run(self) -> None:
        """
        Start audio recording and speech recognition process.
        Emits signals for detected audio data and transcribed text.
        """

        self.is_recording = True
        with sr.Microphone(sample_rate=44100) as source:
            print(f"Speak now in {self.language}...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
            wav_data = np.frombuffer(audio.get_wav_data(), dtype=np.int16)
            self.audioDataReady.emit(wav_data)
            
            audio = self.remove_silence(audio)
            
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                self.textDetected.emit(text)
            except sr.UnknownValueError:
                self.textDetected.emit(f"Could not understand the audio in {self.language}")
            except sr.RequestError:
                self.textDetected.emit("Error in the voice recognition service")

    def remove_silence(self, audio: sr.AudioData) -> sr.AudioData:
        """
        Remove silence from the recorded audio.

        Args:
            audio: AudioData object containing the recorded audio

        Returns:
            AudioData object with silence removed
        """
        
        wav_io = io.BytesIO(audio.get_wav_data())
        with wave.open(wav_io, 'rb') as wav_file:
            params = wav_file.getparams()
            frames = wav_file.readframes(wav_file.getnframes())
            audio_segment = AudioSegment(
                data=frames,
                sample_width=params.sampwidth,
                frame_rate=params.framerate,
                channels=params.nchannels
            )
            chunks = split_on_silence(audio_segment, min_silence_len=500, silence_thresh=-40)
            output_audio = sum(chunks, AudioSegment.silent(duration=1000))
            wav_io = io.BytesIO()
            output_audio.export(wav_io, format="wav")
            wav_io.seek(0)
            with wave.open(wav_io, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_rate = wav_file.getframerate()
                sample_width = wav_file.getsampwidth()
                return sr.AudioData(frames, sample_rate, sample_width)