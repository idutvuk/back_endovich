"""DB — место, где лежат данные. Здесь: создание соединения и схемы таблиц."""

import sqlite3

DB_PATH = "sons.sqlite3"


def get_connection(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # строки как dict-подобные объекты
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sons (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL,
            age  INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    return conn
