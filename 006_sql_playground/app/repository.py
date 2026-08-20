from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import CosmonautRow, MissionRow
from app.models import (
    Cosmonaut,
    CosmonautCreate,
    CosmonautDetail,
    Mission,
    MissionCreate,
    MissionDetail,
)


def _cosmonaut(row: CosmonautRow) -> Cosmonaut:
    return Cosmonaut(id=row.id, name=row.name, age=row.age, in_space=row.in_space)


def _mission(row: MissionRow) -> Mission:
    return Mission(id=row.id, name=row.name, destination=row.destination, year=row.year)


class CosmonautRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, data: CosmonautCreate) -> Cosmonaut:
        row = CosmonautRow(name=data.name, age=data.age)
        self._session.add(row)
        self._session.commit()
        return _cosmonaut(row)

    def get(self, cosmonaut_id: int) -> CosmonautDetail | None:
        row = self._session.get(CosmonautRow, cosmonaut_id)
        if row is None:
            return None
        return CosmonautDetail(
            **_cosmonaut(row).model_dump(),
            missions=[_mission(m) for m in row.missions],
        )

    def list_all(self) -> list[Cosmonaut]:
        rows = self._session.scalars(select(CosmonautRow)).all()
        return [_cosmonaut(row) for row in rows]


class MissionRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, data: MissionCreate) -> Mission:
        row = MissionRow(name=data.name, destination=data.destination, year=data.year)
        self._session.add(row)
        self._session.commit()
        return _mission(row)

    def get(self, mission_id: int) -> MissionDetail | None:
        row = self._session.get(MissionRow, mission_id)
        if row is None:
            return None
        return MissionDetail(
            **_mission(row).model_dump(),
            crew=[_cosmonaut(c) for c in row.crew],
        )

    def list_all(self) -> list[Mission]:
        rows = self._session.scalars(select(MissionRow)).all()
        return [_mission(row) for row in rows]

    def crew_ids(self, mission_id: int) -> list[int]:
        row = self._session.get(MissionRow, mission_id)
        return [c.id for c in row.crew] if row else []

    def assign(self, mission_id: int, cosmonaut_id: int) -> None:
        mission = self._session.get(MissionRow, mission_id)
        cosmonaut = self._session.get(CosmonautRow, cosmonaut_id)
        if mission is not None and cosmonaut is not None:
            mission.crew.append(cosmonaut)  # строка в mission_crew
            self._session.commit()

    def dismiss(self, mission_id: int, cosmonaut_id: int) -> None:
        mission = self._session.get(MissionRow, mission_id)
        cosmonaut = self._session.get(CosmonautRow, cosmonaut_id)
        if mission is not None and cosmonaut is not None and cosmonaut in mission.crew:
            mission.crew.remove(cosmonaut)
            self._session.commit()
