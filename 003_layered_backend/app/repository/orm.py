"""REPOSITORY — классы, которые разговаривают с БД.

Реализация контракта CosmonautRepo из core поверх SQLAlchemy.
Все запросы в базу — только здесь.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import Cosmonaut, CosmonautCreate
from app.repository.db import CosmonautRow


def _to_model(row: CosmonautRow) -> Cosmonaut:
    return Cosmonaut(id=row.id, name=row.name, age=row.age, in_space=row.in_space)


class SqlAlchemyCosmonautRepo:
    """Живёт в рамках одной сессии (одного HTTP-запроса)."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, cosmonaut: CosmonautCreate) -> Cosmonaut:
        row = CosmonautRow(name=cosmonaut.name, age=cosmonaut.age)
        self._session.add(row)
        self._session.commit()
        return _to_model(row)

    def get(self, cosmonaut_id: int) -> Cosmonaut | None:
        row = self._session.get(CosmonautRow, cosmonaut_id)
        return _to_model(row) if row else None

    def list_all(self, in_space: bool | None = None) -> list[Cosmonaut]:
        query = select(CosmonautRow)
        if in_space is not None:
            query = query.where(CosmonautRow.in_space == in_space)
        rows = self._session.scalars(query).all()
        return [_to_model(row) for row in rows]

    def set_in_space(self, cosmonaut_id: int, in_space: bool) -> None:
        row = self._session.get(CosmonautRow, cosmonaut_id)
        if row is not None:
            row.in_space = in_space
            self._session.commit()

    def delete(self, cosmonaut_id: int) -> bool:
        row = self._session.get(CosmonautRow, cosmonaut_id)
        if row is None:
            return False
        self._session.delete(row)
        self._session.commit()
        return True


    def change_age(self, cosmonaut_id: int, new_age: int) -> None:
        row = self._session.get(CosmonautRow, cosmonaut_id)
        if row is not None:
            row.age = new_age
            self._session.commit()

