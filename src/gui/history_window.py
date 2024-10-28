from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                            QPushButton, QTableWidget, QTableWidgetItem, QLabel,
                            QComboBox, QHeaderView, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from datetime import datetime

class TranslationHistoryWindow(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()
        self.load_translations()
        
    def setup_ui(self):
        self.setWindowTitle("Translation History")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in translations...")
        self.search_input.textChanged.connect(self.delayed_search)
        search_layout.addWidget(self.search_input)
        
        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItems(["All Languages", "Italian", "English", "Spanish", "French", "German"])
        self.source_lang_combo.currentTextChanged.connect(self.load_translations)
        search_layout.addWidget(QLabel("Source:"))
        search_layout.addWidget(self.source_lang_combo)
        
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems(["All Languages", "Italian", "English", "Spanish", "French", "German"])
        self.target_lang_combo.currentTextChanged.connect(self.load_translations)
        search_layout.addWidget(QLabel("Target:"))
        search_layout.addWidget(self.target_lang_combo)
        
        layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Source Text", "Target Text", 
            "Source Lang", "Target Lang", "Timestamp"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(delete_button)
        
        copy_source_button = QPushButton("Copy Source")
        copy_source_button.clicked.connect(lambda: self.copy_text(1))
        button_layout.addWidget(copy_source_button)
        
        copy_target_button = QPushButton("Copy Translation")
        copy_target_button.clicked.connect(lambda: self.copy_text(2))
        button_layout.addWidget(copy_target_button)
        
        layout.addLayout(button_layout)
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.load_translations)
        
    def delayed_search(self):
        self.search_timer.start(300) 
        
    def load_translations(self):
        search_text = self.search_input.text()
        source_lang = None if self.source_lang_combo.currentText() == "All Languages" else self.source_lang_combo.currentText()
        target_lang = None if self.target_lang_combo.currentText() == "All Languages" else self.target_lang_combo.currentText()
        
        results = self.db_manager.search_translations(
            search_text=search_text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        self.table.setRowCount(len(results))
        for i, row in enumerate(results):
            for j, value in enumerate(row):
                if j == 5: 
                    value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  
                self.table.setItem(i, j, item)
    
    def delete_selected(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        for row in sorted(selected_rows, reverse=True):
            translation_id = int(self.table.item(row, 0).text())
            self.db_manager.delete_translation(translation_id)
            self.table.removeRow(row)
    
    def copy_text(self, column):
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            text = self.table.item(row, column).text()
            QApplication.clipboard().setText(text)