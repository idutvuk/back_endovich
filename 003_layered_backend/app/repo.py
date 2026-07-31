"""REPO — классы, которые разговаривают с БД. SQL живёт только здесь.

Интерфейс (Protocol) отделяет ЛОГИКУ от конкретной базы:
логика знает только контракт CosmonautRepo, а не sqlite.
"""

import sqlite3
from typing import Protocol

from app.schemas import Cosmonaut, CosmonautCreate


class CosmonautRepo(Protocol):
    """Интерфейс репозитория. Логика зависит от него, а не от sqlite."""

    def add(self, cosmonaut: CosmonautCreate) -> Cosmonaut: ...

    def get(self, cosmonaut_id: int) -> Cosmonaut | None: ...

    def list_all(self) -> list[Cosmonaut]: ...

    def set_in_space(self, cosmonaut_id: int, in_space: bool) -> None: ...

    def delete(self, cosmonaut_id: int) -> bool: ...


def _to_model(row: sqlite3.Row) -> Cosmonaut:
    return Cosmonaut(
        id=row["id"], name=row["name"], age=row["age"], in_space=bool(row["in_space"])
    )


class SqliteCosmonautRepo:
    """Реализация интерфейса поверх sqlite. Запросы в базу — только тут."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(self, cosmonaut: CosmonautCreate) -> Cosmonaut:
        cur = self._conn.execute(
            "INSERT INTO cosmonauts (name, age) VALUES (?, ?)",
            (cosmonaut.name, cosmonaut.age),
        )
        self._conn.commit()
        return Cosmonaut(id=cur.lastrowid, name=cosmonaut.name, age=cosmonaut.age)

    def get(self, cosmonaut_id: int) -> Cosmonaut | None:
        row = self._conn.execute(
            "SELECT id, name, age, in_space FROM cosmonauts WHERE id = ?",
            (cosmonaut_id,),
        ).fetchone()
        return _to_model(row) if row else None

    def list_all(self) -> list[Cosmonaut]:
        rows = self._conn.execute(
            "SELECT id, name, age, in_space FROM cosmonauts"
        ).fetchall()
        return [_to_model(row) for row in rows]

    def set_in_space(self, cosmonaut_id: int, in_space: bool) -> None:
        self._conn.execute(
            "UPDATE cosmonauts SET in_space = ? WHERE id = ?",
            (int(in_space), cosmonaut_id),
        )
        self._conn.commit()

    def delete(self, cosmonaut_id: int) -> bool:
        cur = self._conn.execute(
            "DELETE FROM cosmonauts WHERE id = ?", (cosmonaut_id,)
        )
        self._conn.commit()
        return cur.rowcount > 0
