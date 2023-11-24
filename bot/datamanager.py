# bot/datamanager.py

import sqlite3
from sqlite3 import Error
import logging
class DatabaseManager:
    def __init__(self, db_file='user_data.db'):
        self.db_file = db_file

    def create_connection(self):
        connection = None
        try:
            connection = sqlite3.connect(self.db_file)
            logging.info(f"Connection to SQLite database successful.")
            return connection
        except Error as e:
            logging.error(f"Error: {e}")
        return connection

    def create_user_data_table(self, user_id):
        """Create a table for user data if it doesn't exist."""
        table_name = f"user_{user_id}"
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            data_id INTEGER PRIMARY KEY,
            response TEXT,
            lang TEXT
        );
        """
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(create_table_sql)
                connection.commit()
                cursor.close()
            except Error as e:
                logging.error(f"Error: {e}")
            finally:
                if connection:
                    connection.close()

    def store_user_data(self, user_id, data_id, response, lang):
        """Store user data in the user-specific table with a maximum of 20 entries."""
        table_name = f"user_{user_id}"
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                self.create_user_data_table(user_id)
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                entry_count = cursor.fetchone()[0]
                if entry_count >= 20:
                    cursor.execute(f"DELETE FROM {table_name} WHERE data_id = (SELECT MIN(data_id) FROM {table_name})")
                cursor.execute(f"INSERT INTO {table_name} (data_id, response, lang) VALUES (?, ?, ?)", (data_id, response, lang))
                connection.commit()
                logging.info(f"data stored")
                cursor.close()
            except Error as e:
                logging.error(f"Error: {e}")
            finally:
                if connection:
                    connection.close()

    def retrieve_user_data(self, user_id):
        """Retrieve user data from the user-specific table."""
        table_name = f"user_{user_id}"
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                table_exists = cursor.fetchone()
                if table_exists:
                    cursor.execute(f"SELECT data_id, response, lang FROM {table_name}")
                    result = cursor.fetchall()
                    cursor.close()
                    return result
                else:
                    logging.warning(f"Table {table_name} does not exist.")
                    cursor.close()
                    return None
            except Error as e:
                logging.error(f"Error: {e}")
            finally:
                if connection:
                    connection.close()
        return None

    def retrieve_user_data_by_data_id(self, user_id, data_id):
        """Retrieve user data from the user-specific table based on data_id."""
        table_name = f"user_{user_id}"
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                table_exists = cursor.fetchone()
                if table_exists:
                    cursor.execute(f"SELECT response, lang FROM {table_name} WHERE data_id=?", (data_id,))
                    result = cursor.fetchone()
                    cursor.close()
                    return result
                else:
                    logging.warning(f"Table {table_name} does not exist.")
                    cursor.close()
                    return None
            except Error as e:
                logging.error(f"Error: {e}")
            finally:
                if connection:
                    connection.close()
        return None
