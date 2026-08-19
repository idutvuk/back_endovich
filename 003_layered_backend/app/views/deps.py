"""Зависимости для FastAPI Depends: сборка цепочки DB -> REPO -> LOGIC
на каждый запрос."""

from collections.abc import Iterator

from fastapi import Depends, Header, HTTPException, status
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


COMMANDER_KEY = "glavkosmos"


def require_commander(x_commander_key: str = Header(default="")) -> None:
    """Пускает дальше только с заголовком X-Commander-Key: glavkosmos."""
    if x_commander_key != COMMANDER_KEY:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Только для командира: нужен заголовок X-Commander-Key",
        )
