"""REPOSITORY — конкретные репозитории поверх SQLAlchemy.

Все запросы в базу — только здесь. Репозитории не коммитят:
транзакция — на весь HTTP-запрос (см. views/deps.py), поэтому
составные операции («списать ресурсы + создать ракету») атомарны.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import (
    Cosmonaut,
    CosmonautCreate,
    Mission,
    MissionCreate,
    MissionStatus,
    Orbit,
    Resource,
    Rocket,
    RocketStatus,
    RocketType,
    RocketTypeCreate,
    Station,
    StationCreate,
)
from app.core.zodiac import zodiac_sign
from app.repository.db import (
    CosmonautRow,
    MissionRow,
    ResourceRow,
    RocketRow,
    RocketTypeRow,
    StationRow,
)


def _cosmonaut(row: CosmonautRow) -> Cosmonaut:
    return Cosmonaut(
        id=row.id,
        name=row.name,
        country=row.country,
        birth_date=row.birth_date,
        zodiac=zodiac_sign(row.birth_date),
        in_space=row.in_space,
        station_id=row.station_id,
        rocket_id=row.rocket_id,
    )


def _station(row: StationRow) -> Station:
    return Station(
        id=row.id,
        name=row.name,
        orbit=Orbit(radius_km=row.radius_km, phase_deg=row.phase_deg, epoch=row.epoch),
        oxygen=row.oxygen,
    )


def _rocket_type(row: RocketTypeRow) -> RocketType:
    return RocketType(
        id=row.id, code=row.code, name=row.name, kind=row.kind,
        capacity=row.capacity, cost=row.cost,
    )


def _rocket(row: RocketRow, mission_id: int | None) -> Rocket:
    orbit = None
    if row.radius_km is not None and row.epoch is not None:
        orbit = Orbit(radius_km=row.radius_km, phase_deg=row.phase_deg or 0, epoch=row.epoch)
    return Rocket(
        id=row.id,
        name=row.name,
        type=_rocket_type(row.type),
        status=RocketStatus(row.status),
        station_id=row.station_id,
        mission_id=mission_id,
        orbit=orbit,
    )


def _mission(row: MissionRow) -> Mission:
    return Mission(
        id=row.id,
        name=row.name,
        status=MissionStatus(row.status),
        cargo_tons=row.cargo_tons,
        reward=row.reward,
        starts_at=row.starts_at,
        deadline=row.deadline,
        station_id=row.station_id,
        rocket_id=row.rocket_id,
        crew=[_cosmonaut(c) for c in row.crew],
    )


class CosmonautRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, data: CosmonautCreate) -> Cosmonaut:
        row = CosmonautRow(name=data.name, country=data.country, birth_date=data.birth_date)
        self._session.add(row)
        self._session.flush()
        return _cosmonaut(row)

    def get(self, cosmonaut_id: int) -> Cosmonaut | None:
        row = self._session.get(CosmonautRow, cosmonaut_id)
        return _cosmonaut(row) if row else None

    def list_all(
        self,
        name: str | None = None,
        country: str | None = None,
        in_space: bool | None = None,
        station_id: int | None = None,
        rocket_id: int | None = None,
    ) -> list[Cosmonaut]:
        query = select(CosmonautRow).order_by(CosmonautRow.name)
        if name:
            query = query.where(CosmonautRow.name.ilike(f"%{name}%"))
        if country:
            query = query.where(CosmonautRow.country.ilike(f"%{country}%"))
        if in_space is not None:
            query = query.where(CosmonautRow.in_space == in_space)
        if station_id is not None:
            query = query.where(CosmonautRow.station_id == station_id)
        if rocket_id is not None:
            query = query.where(CosmonautRow.rocket_id == rocket_id)
        return [_cosmonaut(row) for row in self._session.scalars(query)]

    def set_location(
        self, cosmonaut_id: int, in_space: bool,
        station_id: int | None, rocket_id: int | None,
    ) -> None:
        row = self._session.get(CosmonautRow, cosmonaut_id)
        if row is not None:
            row.in_space = in_space
            row.station_id = station_id
            row.rocket_id = rocket_id

    def delete(self, cosmonaut_id: int) -> bool:
        row = self._session.get(CosmonautRow, cosmonaut_id)
        if row is None:
            return False
        self._session.delete(row)
        return True


class StationRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, data: StationCreate) -> Station:
        row = StationRow(
            name=data.name,
            radius_km=data.orbit.radius_km,
            phase_deg=data.orbit.phase_deg,
            epoch=data.orbit.epoch,
            oxygen=data.oxygen,
        )
        self._session.add(row)
        self._session.flush()
        return _station(row)

    def get(self, station_id: int) -> Station | None:
        row = self._session.get(StationRow, station_id)
        return _station(row) if row else None

    def list_all(self) -> list[Station]:
        rows = self._session.scalars(select(StationRow).order_by(StationRow.radius_km))
        return [_station(row) for row in rows]

    def set_oxygen(self, station_id: int, oxygen: float) -> None:
        row = self._session.get(StationRow, station_id)
        if row is not None:
            row.oxygen = oxygen


class RocketRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    # --- типы ---

    def add_type(self, data: RocketTypeCreate) -> RocketType:
        row = RocketTypeRow(
            code=data.code, name=data.name, kind=data.kind,
            capacity=data.capacity, cost=data.cost,
        )
        self._session.add(row)
        self._session.flush()
        return _rocket_type(row)

    def get_type_by_code(self, code: str) -> RocketType | None:
        row = self._session.scalar(select(RocketTypeRow).where(RocketTypeRow.code == code))
        return _rocket_type(row) if row else None

    def list_types(self) -> list[RocketType]:
        rows = self._session.scalars(select(RocketTypeRow).order_by(RocketTypeRow.id))
        return [_rocket_type(row) for row in rows]

    # --- ракеты ---

    def add(self, name: str, type_id: int) -> Rocket:
        row = RocketRow(name=name, type_id=type_id, status=RocketStatus.CREATED)
        self._session.add(row)
        self._session.flush()
        return _rocket(row, mission_id=None)

    def get(self, rocket_id: int) -> Rocket | None:
        row = self._session.get(RocketRow, rocket_id)
        return _rocket(row, self._mission_id(rocket_id)) if row else None

    def list_all(self, status: RocketStatus | None = None) -> list[Rocket]:
        query = select(RocketRow).order_by(RocketRow.id.desc())
        if status is not None:
            query = query.where(RocketRow.status == status)
        rows = self._session.scalars(query).all()
        mission_ids = self._mission_ids([row.id for row in rows])
        return [_rocket(row, mission_ids.get(row.id)) for row in rows]

    def set_status(self, rocket_id: int, status: RocketStatus) -> None:
        row = self._session.get(RocketRow, rocket_id)
        if row is not None:
            row.status = status

    def set_station(self, rocket_id: int, station_id: int | None) -> None:
        row = self._session.get(RocketRow, rocket_id)
        if row is not None:
            row.station_id = station_id

    def set_orbit(self, rocket_id: int, orbit: Orbit | None) -> None:
        row = self._session.get(RocketRow, rocket_id)
        if row is None:
            return
        if orbit is None:
            row.radius_km = row.phase_deg = row.epoch = None
        else:
            row.radius_km = orbit.radius_km
            row.phase_deg = orbit.phase_deg
            row.epoch = orbit.epoch

    def _mission_id(self, rocket_id: int) -> int | None:
        return self._session.scalar(
            select(MissionRow.id).where(MissionRow.rocket_id == rocket_id)
        )

    def _mission_ids(self, rocket_ids: list[int]) -> dict[int, int]:
        if not rocket_ids:
            return {}
        pairs = self._session.execute(
            select(MissionRow.rocket_id, MissionRow.id).where(MissionRow.rocket_id.in_(rocket_ids))
        )
        return {rocket_id: mission_id for rocket_id, mission_id in pairs}


class MissionRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, data: MissionCreate) -> Mission:
        row = MissionRow(
            name=data.name,
            status=MissionStatus.OPEN,
            cargo_tons=data.cargo_tons,
            reward=data.reward,
            starts_at=data.starts_at,
            deadline=data.deadline,
            station_id=data.station_id,
        )
        self._session.add(row)
        self._session.flush()
        return _mission(row)

    def get(self, mission_id: int) -> Mission | None:
        row = self._session.get(MissionRow, mission_id)
        return _mission(row) if row else None

    def list_all(self, status: MissionStatus | None = None) -> list[Mission]:
        query = select(MissionRow).order_by(MissionRow.id.desc())
        if status is not None:
            query = query.where(MissionRow.status == status)
        return [_mission(row) for row in self._session.scalars(query).unique()]

    def set_status(self, mission_id: int, status: MissionStatus) -> None:
        row = self._session.get(MissionRow, mission_id)
        if row is not None:
            row.status = status

    def assign(self, mission_id: int, rocket_id: int | None, crew_ids: list[int]) -> None:
        row = self._session.get(MissionRow, mission_id)
        if row is None:
            return
        row.rocket_id = rocket_id
        row.crew = [
            self._session.get(CosmonautRow, cosmonaut_id) for cosmonaut_id in crew_ids
        ]


class ResourceRepo:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Resource]:
        rows = self._session.scalars(select(ResourceRow).order_by(ResourceRow.name))
        return [Resource(name=row.name, amount=row.amount) for row in rows]

    def amount(self, name: str) -> float:
        row = self._session.get(ResourceRow, name)
        return row.amount if row else 0.0

    def deposit(self, name: str, amount: float) -> Resource:
        row = self._session.get(ResourceRow, name)
        if row is None:
            row = ResourceRow(name=name, amount=0)
            self._session.add(row)
        row.amount += amount
        self._session.flush()
        return Resource(name=row.name, amount=row.amount)

    def withdraw(self, name: str, amount: float) -> None:
        """Вызывающий обязан заранее проверить остаток (см. RocketService.build)."""
        row = self._session.get(ResourceRow, name)
        if row is not None:
            row.amount = max(0.0, row.amount - amount)
