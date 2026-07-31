"""REPO — классы, которые разговаривают с БД. SQL живёт только здесь.

Интерфейс (Protocol) отделяет ЛОГИКУ от конкретной базы:
логика знает только контракт SonRepo, а не sqlite.
"""

import sqlite3
from typing import Protocol

from app.schemas import Son, SonCreate


class SonRepo(Protocol):
    """Интерфейс репозитория. Логика зависит от него, а не от sqlite."""

    def add(self, son: SonCreate) -> Son: ...

    def get(self, son_id: int) -> Son | None: ...

    def list_all(self) -> list[Son]: ...

    def delete(self, son_id: int) -> bool: ...


class SqliteSonRepo:
    """Реализация интерфейса поверх sqlite. Запросы в базу — только тут."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, son: SonCreate) -> Son:
        cur = self._conn.execute(
            "INSERT INTO sons (name, age) VALUES (?, ?)",
            (son.name, son.age),
        )
        self._conn.commit()
        return Son(id=cur.lastrowid, name=son.name, age=son.age)

    def get(self, son_id: int) -> Son | None:
        row = self._conn.execute(
            "SELECT id, name, age FROM sons WHERE id = ?", (son_id,)
        ).fetchone()
        return Son(**row) if row else None

    def list_all(self) -> list[Son]:
        rows = self._conn.execute("SELECT id, name, age FROM sons").fetchall()
        return [Son(**row) for row in rows]

    def delete(self, son_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM sons WHERE id = ?", (son_id,))
        self._conn.commit()
        return cur.rowcount > 0
