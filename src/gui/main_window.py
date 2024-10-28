from PyQt6.QtWidgets import (QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QComboBox, QStatusBar, QFrame)
from PyQt6.QtGui import QFont, QIcon, QPainter
from PyQt6.QtCore import Qt
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
import numpy as np
from src.audio.recorder import AudioThread
from src.translator.model import TranslatorModel
from src.database.manager import DatabaseManager

class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vocal Translator")
        self.setGeometry(100, 100, 800, 600)

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
            color: black;
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
            background-color: white;
            color: black;
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
            min-width: 100px;
        }
        QComboBox::drop-down {
            border: none;
            background-color: transparent;
        }
        QComboBox::down-arrow {
            image: none;
            border: none;
            width: 20px;
            height: 20px;
        }
        QComboBox::down-arrow:on {
            top: 1px;
            left: 1px;
        }
        QComboBox QAbstractItemView {
            background-color: white;
            color: black;
            selection-background-color: #e0e0e0;
            selection-color: black;
            border: 1px solid #ddd;
        }
        QChartView {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    """)

        self.audio_thread = AudioThread(self)
        self.audio_thread.textDetected.connect(self.on_text_detected)
        self.audio_thread.audioDataReady.connect(self.update_waveform)

        self.translator_model = TranslatorModel()
        self.db_manager = DatabaseManager()
        
        self.setup_audio_visualizer()
        self.setup_ui()

        self.statusBar().showMessage('Ready')

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        title_label = QLabel("Voice Translator")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.layout.addWidget(title_label)

        self.layout.addSpacing(20)

        source_lang_layout = QHBoxLayout()
        source_lang_label = QLabel("Source Language:")
        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItems(["Italian", "English", "Spanish", "French", "German"])
        source_lang_layout.addWidget(source_lang_label)
        source_lang_layout.addWidget(self.source_lang_combo)
        self.layout.addLayout(source_lang_layout)

        self.layout.addWidget(self.chart_view)

        input_layout = QHBoxLayout()
        self.record_button = QPushButton("Record")
        self.record_button.setIcon(QIcon("assets/mic_icon.png"))
        self.record_button.clicked.connect(self.start_recording)
        input_layout.addWidget(self.record_button)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Input text will appear here...")
        input_layout.addWidget(self.input_text)

        self.layout.addLayout(input_layout)

        self.layout.addSpacing(20)

        translate_layout = QHBoxLayout()
        target_lang_label = QLabel("Target Language:")
        self.target_lang_combo = QComboBox()
        
        self.translate_button = QPushButton("Translate")
        self.translate_button.setIcon(QIcon("assets/translate_icon.png"))
        self.translate_button.clicked.connect(self.translate_text)
        
        translate_layout.addWidget(self.translate_button)
        translate_layout.addWidget(target_lang_label)
        translate_layout.addWidget(self.target_lang_combo)
        self.layout.addLayout(translate_layout)

        self.source_lang_combo.currentTextChanged.connect(self.update_target_languages)
        self.update_target_languages(self.source_lang_combo.currentText())

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

    def setup_audio_visualizer(self):
        self.audio_chart = QChart()
        self.audio_series = QLineSeries()
        
        pen = self.audio_series.pen()
        pen.setWidth(2)
        pen.setColor(Qt.GlobalColor.darkBlue)  
        self.audio_series.setPen(pen)
        
        self.axis_x = QValueAxis()
        self.axis_y = QValueAxis()
        self.axis_x.setRange(0, 1000)
        self.axis_y.setRange(-1, 1)
        
        self.axis_x.setLabelsVisible(False)  
        self.axis_y.setLabelsVisible(False) 
        
        self.audio_chart.addSeries(self.audio_series)
        self.audio_chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.audio_chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        
        self.audio_series.attachAxis(self.axis_x)
        self.audio_series.attachAxis(self.axis_y)
        
        self.audio_chart.setTitle("Audio Waveform")
        self.audio_chart.legend().hide()
        
        self.audio_chart.setBackgroundBrush(Qt.GlobalColor.white)
        self.audio_chart.setBackgroundVisible(True)
        self.audio_chart.setPlotAreaBackgroundVisible(True)
        self.audio_chart.setPlotAreaBackgroundBrush(Qt.GlobalColor.white)
        
        self.axis_x.setGridLineVisible(False)
        self.axis_y.setGridLineVisible(True)
        self.axis_y.setGridLineColor(Qt.GlobalColor.lightGray)
        
        self.chart_view = QChartView(self.audio_chart)
        self.chart_view.setMinimumHeight(150)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

    def update_waveform(self, audio_data):
        normalized_data = audio_data / np.max(np.abs(audio_data))
        
        self.audio_series.clear()
        step = len(normalized_data) // 1000
        for i, value in enumerate(normalized_data[::step][:1000]):
            self.audio_series.append(i, value)
            
        self.audio_chart.update()

    def start_recording(self):
        self.record_button.setEnabled(False)
        self.record_button.setText("Recording...")
        self.statusBar().showMessage('Recording...')
        self.audio_series.clear()
        self.audio_thread.start()

    def on_text_detected(self, text):
        self.input_text.setPlainText(text)
        self.record_button.setEnabled(True)
        self.record_button.setText("Record")
        self.statusBar().showMessage('Recording completed')

    

    def update_target_languages(self, source_lang):
        self.target_lang_combo.clear()
        supported_pairs = [target for (source, target) in self.translator_model.language_pairs.keys() 
                         if source.lower() == source_lang.lower()]
        self.target_lang_combo.addItems([lang.capitalize() for lang in supported_pairs])

    def translate_text(self):
        source_lang = self.source_lang_combo.currentText().lower()
        target_lang = self.target_lang_combo.currentText().lower()
        input_text = self.input_text.toPlainText()
        
        if input_text:
            self.statusBar().showMessage('Translating...')
            translation = self.translator_model.translate(input_text, source_lang, target_lang)
            self.output_text.setPlainText(translation)
            self.statusBar().showMessage('Translation completed')

    def save_translation(self):
        source_text = self.input_text.toPlainText()
        target_text = self.output_text.toPlainText()
        source_lang = self.source_lang_combo.currentText().lower()
        target_lang = self.target_lang_combo.currentText().lower()
        
        if source_text and target_text:
            self.db_manager.save_translation(source_text, target_text, source_lang, target_lang)
            self.statusBar().showMessage('Translation saved to database')