"""Сборка цепочки DB -> REPO -> LOGIC на каждый запрос.

Транзакция — на весь запрос: коммит после успешного выхода из view,
при исключении сессия закрывается без коммита (откат).
"""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.services import (
    CosmonautService,
    MapService,
    MissionService,
    RocketService,
    StationService,
)
from app.repository.db import SessionLocal
from app.repository.orm import CosmonautRepo, MissionRepo, ResourceRepo, RocketRepo, StationRepo


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
        session.commit()


SessionDep = Annotated[Session, Depends(get_session)]


def get_cosmonaut_service(session: SessionDep) -> CosmonautService:
    return CosmonautService(CosmonautRepo(session))


def get_station_service(session: SessionDep) -> StationService:
    return StationService(StationRepo(session))


def get_rocket_service(session: SessionDep) -> RocketService:
    return RocketService(
        RocketRepo(session), ResourceRepo(session), StationRepo(session), CosmonautRepo(session)
    )


def get_mission_service(session: SessionDep) -> MissionService:
    return MissionService(
        MissionRepo(session), RocketRepo(session), CosmonautRepo(session), ResourceRepo(session)
    )


def get_map_service(session: SessionDep) -> MapService:
    return MapService(StationRepo(session), RocketRepo(session))


def get_resource_repo(session: SessionDep) -> ResourceRepo:
    return ResourceRepo(session)


CosmonautsDep = Annotated[CosmonautService, Depends(get_cosmonaut_service)]
StationsDep = Annotated[StationService, Depends(get_station_service)]
RocketsDep = Annotated[RocketService, Depends(get_rocket_service)]
MissionsDep = Annotated[MissionService, Depends(get_mission_service)]
MapDep = Annotated[MapService, Depends(get_map_service)]
ResourcesDep = Annotated[ResourceRepo, Depends(get_resource_repo)]
