from collections.abc import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.repository import CosmonautRepo, MissionRepo
from app.services import BureauService


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


def get_service(session: Session = Depends(get_session)) -> BureauService:
    return BureauService(CosmonautRepo(session), MissionRepo(session))
