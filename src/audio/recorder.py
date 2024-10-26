from PyQt6.QtCore import QThread, pyqtSignal
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import io
import wave
import numpy as np

class AudioThread(QThread):
    textDetected = pyqtSignal(str)
    audioDataReady = pyqtSignal(np.ndarray)  
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        
    def run(self):
        self.is_recording = True
        with sr.Microphone(sample_rate=44100) as source:
            print("Speak now...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
            wav_data = np.frombuffer(audio.get_wav_data(), dtype=np.int16)
            self.audioDataReady.emit(wav_data)
            
            audio = self.remove_silence(audio)
            try:
                text = self.recognizer.recognize_google(audio, language="it-IT")
                self.textDetected.emit(text)
            except sr.UnknownValueError:
                self.textDetected.emit("I didn't understand the audio")
            except sr.RequestError:
                self.textDetected.emit("Error in the voice recognition service")

    def remove_silence(self, audio):
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