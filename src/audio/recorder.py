import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QComboBox
from PyQt6.QtCore import QThread, pyqtSignal
import speech_recognition as sr
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import torch

class AudioThread(QThread):
    textDetected = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.recognizer = sr.Recognizer()

    def run(self):
        with sr.Microphone() as source:
            print("Talk now in Italian...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(audio, language="it-IT")
            self.textDetected.emit(text)
        except sr.UnknownValueError:
            self.textDetected.emit("I didn't understand the audio")
        except sr.RequestError:
            self.textDetected.emit("Error in the voice recognition service")