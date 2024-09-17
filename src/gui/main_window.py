from PyQt6.QtWidgets import (QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QComboBox, QStatusBar, QFrame)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
from src.audio.recorder import AudioThread
from src.translator.model import TranslatorModel
from src.database.manager import DatabaseManager

class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vocal Translator")
        self.setGeometry(100, 100, 600, 400)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTextEdit {
                background-color: white;
                color : black;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLabel {
                font-size: 16px;
                color: #333;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)

        self.centra_widget = QWidget()
        self.setCentralWidget(self.centra_widget)
        self.layout = QVBoxLayout(self.centra_widget)

        self.setup_ui()

        self.audio_thread = AudioThread(self)
        self.audio_thread.textDetected.connect(self.on_text_detected)

        self.translator_model = TranslatorModel()
        self.db_manager = DatabaseManager()

        self.statusBar().showMessage('Ready')

    def setup_ui(self):
        title_label = QLabel("Voice Translator")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.layout.addWidget(title_label)

        self.layout.addSpacing(20)

        input_layout = QHBoxLayout()
        self.record_button = QPushButton("Record")
        self.record_button.setIcon(QIcon("assets/mic_icon.png"))
        self.record_button.clicked.connect(self.start_recording)
        input_layout.addWidget(self.record_button)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Italian text will appear here...")
        input_layout.addWidget(self.input_text)

        self.layout.addLayout(input_layout)

        self.layout.addSpacing(20)

        translate_layout = QHBoxLayout()
        self.translate_button = QPushButton("Translate")
        self.translate_button.setIcon(QIcon("assets/translate_icon.png"))
        self.translate_button.clicked.connect(self.translate_text)
        translate_layout.addWidget(self.translate_button)

        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems(["English", "Spanish", "French", "German"])
        translate_layout.addWidget(self.target_lang_combo)

        self.layout.addLayout(translate_layout)

        self.layout.addSpacing(20)

        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Translation will appear here...")
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)

        self.layout.addSpacing(20)

        save_button = QPushButton("Save Translation")
        save_button.setIcon(QIcon("assets/save_icon.png"))
        save_button.clicked.connect(self.save_translation)
        self.layout.addWidget(save_button)

    def start_recording(self):
        self.record_button.setEnabled(False)
        self.record_button.setText("Recording...")
        self.statusBar().showMessage('Recording...')
        self.audio_thread.start()

    def on_text_detected(self, text):
        self.input_text.setPlainText(text)
        self.record_button.setEnabled(True)
        self.record_button.setText("Record")
        self.statusBar().showMessage('Recording completed')

    def translate_text(self):
        input_text = self.input_text.toPlainText()
        target_lang = self.target_lang_combo.currentText().lower()
        if input_text:
            self.statusBar().showMessage('Translating...')
            translation = self.translator_model.translate(input_text, target_lang)
            self.output_text.setPlainText(translation)
            self.statusBar().showMessage('Translation completed')

    def save_translation(self):
        source_text = self.input_text.toPlainText()
        target_text = self.output_text.toPlainText()
        target_lang = self.target_lang_combo.currentText().lower()
        if source_text and target_text:
            self.db_manager.save_translation(source_text, target_text, 'italian', target_lang)
            self.statusBar().showMessage('Translation saved to database')
