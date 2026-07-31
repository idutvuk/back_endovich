"""REPOSITORY — классы, которые разговаривают с БД. SQL живёт только здесь.

Реализует интерфейс CosmonautRepo из core (сам интерфейс лежит в core —
ядро диктует контракт, реализация подстраивается).
"""

import sqlite3

from app.core.models import Cosmonaut, CosmonautCreate


def _to_model(row: sqlite3.Row) -> Cosmonaut:
    return Cosmonaut(
        id=row["id"], name=row["name"], age=row["age"], in_space=bool(row["in_space"])
    )


class SqliteCosmonautRepo:
    """Реализация CosmonautRepo поверх sqlite. Запросы в базу — только тут."""

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

    def list_all(self, in_space: bool | None = None) -> list[Cosmonaut]:
        query = "SELECT id, name, age, in_space FROM cosmonauts"
        params: tuple = ()
        if in_space is not None:
            query += " WHERE in_space = ?"
            params = (int(in_space),)
        rows = self._conn.execute(query, params).fetchall()
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
