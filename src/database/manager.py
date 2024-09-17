import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='translations.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS translations
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         source_text TEXT,
         target_text TEXT,
         source_lang TEXT,
         target_lang TEXT,
         timestamp DATETIME)
        ''')
        self.conn.commit()

    def save_translation(self, source_text, target_text, source_lang, target_lang):
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        INSERT INTO translations (source_text, target_text, source_lang, target_lang, timestamp)
        VALUES (?, ?, ?, ?, ?)
        ''', (source_text, target_text, source_lang, target_lang, timestamp))
        self.conn.commit()

    def get_translations(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM translations ORDER BY timestamp DESC LIMIT ?', (limit,))
        return cursor.fetchall()

    def __del__(self):
        self.conn.close()