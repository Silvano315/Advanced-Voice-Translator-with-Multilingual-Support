import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple, Union

class DatabaseManager:
    """
    Manages SQLite database operations for storing and retrieving translations.
    Handles database connections, table creation, and CRUD operations.
    """

    def __init__(self, db_name: str = 'translations.db') -> None:
        """
        Initialize database connection and ensure required table exists.

        Args:
            db_name: Name of the SQLite database file (default: 'translations.db')
        """

        self.conn = sqlite3.connect(db_name)
        self.create_table()
        
    def create_table(self) -> None:
        """
        Create translations table and necessary indexes if they don't exist.
        Sets up the schema for storing translation records with timestamps.
        """

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

    def save_translation(self, source_text: str, target_text: str, 
                       source_lang: str, target_lang: str) -> None:
        """
        Save a new translation record to the database.

        Args:
            source_text: Original text
            target_text: Translated text
            source_lang: Source language code
            target_lang: Target language code
        """

        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO translations (source_text, target_text, source_lang, target_lang, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_text, target_text, source_lang, target_lang, timestamp))
        self.conn.commit()

    def search_translations(self, search_text: Optional[str] = None, 
                         source_lang: Optional[str] = None,
                         target_lang: Optional[str] = None, 
                         limit: int = 50) -> List[Tuple[int, str, str, str, str, str]]:
        """
        Search for translations with optional filtering criteria.

        Args:
            search_text: Text to search in source or target text (optional)
            source_lang: Filter by source language (optional)
            target_lang: Filter by target language (optional)
            limit: Maximum number of results to return (default: 50)

        Returns:
            List of tuples containing (id, source_text, target_text, source_lang, target_lang, timestamp)
        """

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

    def delete_translation(self, translation_id: int) -> None:
        """
        Delete a translation record from the database.

        Args:
            translation_id: ID of the translation record to delete
        """

        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM translations WHERE id = ?', (translation_id,))
        self.conn.commit()

    def __del__(self) -> None:
        """
        Clean up database connection when object is destroyed.
        """
        self.conn.close()