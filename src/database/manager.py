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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source_text ON translations(source_text)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_target_text ON translations(target_text)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON translations(timestamp)')
        self.conn.commit()

    def save_translation(self, source_text, target_text, source_lang, target_lang):
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO translations (source_text, target_text, source_lang, target_lang, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_text, target_text, source_lang, target_lang, timestamp))
        self.conn.commit()

    def search_translations(self, search_text=None, source_lang=None, target_lang=None, limit=50):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, source_text, target_text, source_lang, target_lang, timestamp 
            FROM translations WHERE 1=1
        '''
        params = []

        if search_text:
            query += ''' AND (
                source_text LIKE ? OR 
                target_text LIKE ?
            )'''
            search_pattern = f'%{search_text}%'
            params.extend([search_pattern, search_pattern])

        if source_lang:
            query += ' AND source_lang = ?'
            params.append(source_lang.lower())

        if target_lang:
            query += ' AND target_lang = ?'
            params.append(target_lang.lower())

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        return cursor.fetchall()

    def delete_translation(self, translation_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM translations WHERE id = ?', (translation_id,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()