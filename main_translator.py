import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import TranslatorApp

def main():
    app = QApplication(sys.argv)
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()