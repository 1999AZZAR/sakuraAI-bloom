# bot/datamanager.py

import sqlite3
from sqlite3 import Error
import logging

class DatabaseManager:
    def __init__(self, db_file='user_data.db'):
        self.db_file = db_file

    def _execute_query(self, query, params=None):
        try:
            with sqlite3.connect(self.db_file) as connection:
                cursor = connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                connection.commit()
                return cursor
        except Error as e:
            logging.error(f"Error: {e}")

    def create_connection(self):
        return sqlite3.connect(self.db_file)

    def create_user_data_table(self, user_id):
        table_name = f"user_{user_id}"
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            data_id INTEGER PRIMARY KEY,
            response TEXT,
            lang TEXT
        );
        """
        self._execute_query(create_table_sql)

    def store_user_data(self, user_id, data_id, response, lang):
        table_name = f"user_{user_id}"
        self.create_user_data_table(user_id)
        cursor = self._execute_query(f"SELECT COUNT(*) FROM {table_name}")
        entry_count = cursor.fetchone()[0]
        if entry_count >= 20:
            self._execute_query(f"DELETE FROM {table_name} WHERE data_id = (SELECT MIN(data_id) FROM {table_name})")
        self._execute_query(f"INSERT INTO {table_name} (data_id, response, lang) VALUES (?, ?, ?)", (data_id, response, lang))
        logging.info("Data stored")

    def retrieve_user_data(self, user_id):
        table_name = f"user_{user_id}"
        cursor = self._execute_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        table_exists = cursor.fetchone()
        if table_exists:
            cursor = self._execute_query(f"SELECT data_id, response, lang FROM {table_name}")
            result = cursor.fetchall()
            return result
        else:
            logging.warning(f"Table {table_name} does not exist.")
            return None

    def retrieve_user_data_by_data_id(self, user_id, data_id):
        table_name = f"user_{user_id}"
        cursor = self._execute_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        table_exists = cursor.fetchone()

        if table_exists:
            cursor = self._execute_query(f"SELECT response, lang FROM {table_name} WHERE data_id=?", (data_id,))
            result = cursor.fetchone()
            return result
        else:
            logging.warning(f"Table {table_name} does not exist.")
            return None
