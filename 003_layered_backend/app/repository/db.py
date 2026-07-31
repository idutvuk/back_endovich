"""DB — место, где лежат данные. Здесь: создание соединения и схемы таблиц."""

import sqlite3

DB_PATH = "cosmonauts.sqlite3"


def get_connection(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # строки как dict-подобные объекты
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cosmonauts (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            age      INTEGER NOT NULL,
            in_space INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()
    return conn
