"""Зависимости для FastAPI Depends: сборка цепочки DB -> REPO -> LOGIC
на каждый запрос."""

from collections.abc import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.services import CosmonautService, MissionService
from app.repository.db import SessionLocal
from app.repository.orm import SqlAlchemyCosmonautRepo


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


def get_cosmonaut_service(
    session: Session = Depends(get_session),
) -> CosmonautService:
    return CosmonautService(SqlAlchemyCosmonautRepo(session))


def get_mission_service(
    session: Session = Depends(get_session),
) -> MissionService:
    return MissionService(SqlAlchemyCosmonautRepo(session))
