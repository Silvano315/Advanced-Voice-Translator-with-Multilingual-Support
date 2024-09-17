from PyQt6.QtWidgets import QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget
from src.audio.recorder import AudioThread
from src.translator.model import TranslatorModel

class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vocal Translator")
        self.setGeometry(100, 100, 600, 400)

        self.centra_widget = QWidget()
        self.setCentralWidget(self.centra_widget)
        self.layout = QVBoxLayout(self.centra_widget)

        self.setup_ui()

        self.audio_thread = AudioThread(self)
        self.audio_thread.textDetected.connect(self.on_text_detected)

        self.translator_model = TranslatorModel()

    def setup_ui(self):
        self.record_button = QPushButton("Record")
        self.record_button.clicked.connect(self.start_recording)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Italian text will appear here...")

        self.translate_button = QPushButton("Translate")
        self.translate_button.clicked.connect(self.translate_text)

        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("English translation will appear here...")

        self.layout.addWidget(self.record_button)
        self.layout.addWidget(self.input_text)
        self.layout.addWidget(self.translate_button)
        self.layout.addWidget(self.output_text)

    def start_recording(self):
        self.record_button.setEnabled(False)
        self.record_button.setText("Recording in progress...")
        self.audio_thread.start()

    def on_text_detected(self, text):
        self.input_text.setPlainText(text)
        self.record_button.setEnabled(True)
        self.record_button.setText("Record")

    def translate_text(self):
        input_text = self.input_text.toPlainText()
        if input_text:
            translation = self.translator_model.translate(input_text)
            self.output_text.setPlainText(translation)
