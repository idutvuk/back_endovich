"""CORE (LOGIC) — бизнес-логика бюро.

Сверху views (HTTP), снизу конкретные репозитории (SQL).
"""

import math
from datetime import UTC, datetime

from app.core import orbits
from app.core.exceptions import ConflictError, InsufficientResourcesError, NotFoundError
from app.core.models import (
    Cosmonaut,
    CosmonautCreate,
    Mission,
    MissionCreate,
    MissionStatus,
    Orbit,
    OrbitPosition,
    Resource,
    Rocket,
    RocketKind,
    RocketOnMap,
    RocketStatus,
    RocketType,
    RocketTypeCreate,
    Station,
    StationCreate,
    StationOnMap,
    WorldMap,
)
from app.repository.orm import CosmonautRepo, MissionRepo, ResourceRepo, RocketRepo, StationRepo

# Ракета непереиспользуемая: LANDED — терминальный статус.
_ROCKET_TRANSITIONS: dict[RocketStatus, set[RocketStatus]] = {
    RocketStatus.CREATED: {RocketStatus.FLYING},
    RocketStatus.FLYING: {RocketStatus.DOCKED, RocketStatus.DESCENDING},
    RocketStatus.DOCKED: {RocketStatus.DESCENDING},
    RocketStatus.DESCENDING: {RocketStatus.LANDED},
    RocketStatus.LANDED: set(),
}

_MISSION_TRANSITIONS: dict[MissionStatus, set[MissionStatus]] = {
    MissionStatus.OPEN: {MissionStatus.TAKEN, MissionStatus.CANCELLED},
    MissionStatus.TAKEN: {MissionStatus.DONE, MissionStatus.CANCELLED, MissionStatus.OPEN},
    MissionStatus.DONE: set(),
    MissionStatus.CANCELLED: {MissionStatus.OPEN},
}

CREDITS = "кредиты"

# Ракета паркуется чуть ниже станции и позади по фазе.
_PARKING_OFFSET_KM = 200.0
_PARKING_PHASE_LAG_DEG = 30.0


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def position_of(orbit: Orbit, at: datetime | None = None) -> OrbitPosition:
    at = at or _now()
    angle = orbits.angle_at(orbit.radius_km, orbit.phase_deg, orbit.epoch, at)
    rad = math.radians(angle)
    return OrbitPosition(
        at=at,
        radius_km=orbit.radius_km,
        angle_deg=angle,
        x_km=orbit.radius_km * math.cos(rad),
        y_km=orbit.radius_km * math.sin(rad),
        period_min=orbits.orbital_period_s(orbit.radius_km) / 60.0,
    )


class CosmonautService:
    def __init__(self, repo: CosmonautRepo) -> None:
        self._repo = repo

    def enroll(self, data: CosmonautCreate) -> Cosmonaut:
        normalized = data.model_copy(update={"name": data.name.strip()})
        return self._repo.add(normalized)

    def find(self, cosmonaut_id: int) -> Cosmonaut:
        cosmonaut = self._repo.get(cosmonaut_id)
        if cosmonaut is None:
            raise NotFoundError("Космонавт", cosmonaut_id)
        return cosmonaut

    def roster(self, **filters: object) -> list[Cosmonaut]:
        return self._repo.list_all(**filters)

    def expel(self, cosmonaut_id: int) -> None:
        if self.find(cosmonaut_id).in_space:
            raise ConflictError(f"Космонавт #{cosmonaut_id} на орбите — сначала верните его")
        self._repo.delete(cosmonaut_id)


class StationService:
    def __init__(self, repo: StationRepo) -> None:
        self._repo = repo

    def build(self, data: StationCreate) -> Station:
        return self._repo.add(data)

    def find(self, station_id: int) -> Station:
        station = self._repo.get(station_id)
        if station is None:
            raise NotFoundError("Станция", station_id)
        return station

    def list_all(self) -> list[Station]:
        return self._repo.list_all()

    def position(self, station_id: int, at: datetime | None = None) -> OrbitPosition:
        return position_of(self.find(station_id).orbit, at)

    def set_oxygen(self, station_id: int, oxygen: float) -> Station:
        self.find(station_id)
        self._repo.set_oxygen(station_id, oxygen)
        return self.find(station_id)


class RocketService:
    def __init__(
        self, rockets: RocketRepo, resources: ResourceRepo,
        stations: StationRepo, cosmonauts: CosmonautRepo,
    ) -> None:
        self._rockets = rockets
        self._resources = resources
        self._stations = stations
        self._cosmonauts = cosmonauts

    # --- типы (N типов, не только два) ---

    def add_type(self, data: RocketTypeCreate) -> RocketType:
        if self._rockets.get_type_by_code(data.code) is not None:
            raise ConflictError(f"Тип ракеты «{data.code}» уже существует")
        return self._rockets.add_type(data)

    def list_types(self) -> list[RocketType]:
        return self._rockets.list_types()

    # --- постройка за ресурсы ---

    def build(self, type_code: str, name: str | None = None) -> Rocket:
        rocket_type = self._rockets.get_type_by_code(type_code)
        if rocket_type is None:
            raise NotFoundError("Тип ракеты", type_code)

        missing = {
            resource: need - self._resources.amount(resource)
            for resource, need in rocket_type.cost.items()
            if self._resources.amount(resource) < need
        }
        if missing:
            raise InsufficientResourcesError(missing)

        for resource, need in rocket_type.cost.items():
            self._resources.withdraw(resource, need)

        return self._rockets.add(name or rocket_type.name, rocket_type.id)

    # --- жизненный цикл (непереиспользуемая ракета) ---

    def find(self, rocket_id: int) -> Rocket:
        rocket = self._rockets.get(rocket_id)
        if rocket is None:
            raise NotFoundError("Ракета", rocket_id)
        return rocket

    def list_all(self, status: RocketStatus | None = None) -> list[Rocket]:
        return self._rockets.list_all(status)

    def launch(self, rocket_id: int, station_id: int) -> Rocket:
        rocket = self._checked_transition(rocket_id, RocketStatus.FLYING)
        station = self._stations.get(station_id)
        if station is None:
            raise NotFoundError("Станция", station_id)

        parking = Orbit(
            radius_km=station.orbit.radius_km - _PARKING_OFFSET_KM,
            phase_deg=(station.orbit.phase_deg - _PARKING_PHASE_LAG_DEG) % 360,
            epoch=station.orbit.epoch,
        )
        self._rockets.set_status(rocket_id, RocketStatus.FLYING)
        self._rockets.set_station(rocket_id, station_id)
        self._rockets.set_orbit(rocket_id, parking)
        self._board_crew(rocket)
        return self.find(rocket_id)

    def dock(self, rocket_id: int) -> Rocket:
        rocket = self._checked_transition(rocket_id, RocketStatus.DOCKED)
        if rocket.station_id is None:
            raise ConflictError(f"Ракете #{rocket_id} не назначена станция")
        station = self._stations.get(rocket.station_id)
        assert station is not None

        self._rockets.set_status(rocket_id, RocketStatus.DOCKED)
        self._rockets.set_orbit(rocket_id, station.orbit)
        # Экипаж переходит на станцию
        for cosmonaut in self._cosmonauts.list_all(rocket_id=rocket_id):
            self._cosmonauts.set_location(
                cosmonaut.id, in_space=True, station_id=station.id, rocket_id=None
            )
        return self.find(rocket_id)

    def descend(self, rocket_id: int, crew_ids: list[int] | None = None) -> Rocket:
        """Спуск. Можно забрать со станции экипаж (crew_ids) на Землю."""
        rocket = self._checked_transition(rocket_id, RocketStatus.DESCENDING)
        for cosmonaut_id in crew_ids or []:
            cosmonaut = self._cosmonauts.get(cosmonaut_id)
            if cosmonaut is None:
                raise NotFoundError("Космонавт", cosmonaut_id)
            if cosmonaut.station_id != rocket.station_id:
                raise ConflictError(
                    f"Космонавт #{cosmonaut_id} не на станции #{rocket.station_id}"
                )
            self._cosmonauts.set_location(
                cosmonaut_id, in_space=True, station_id=None, rocket_id=rocket_id
            )
        self._rockets.set_status(rocket_id, RocketStatus.DESCENDING)
        self._rockets.set_station(rocket_id, None)
        return self.find(rocket_id)

    def land(self, rocket_id: int) -> Rocket:
        self._checked_transition(rocket_id, RocketStatus.LANDED)
        self._rockets.set_status(rocket_id, RocketStatus.LANDED)
        self._rockets.set_orbit(rocket_id, None)
        # Все, кто был на борту, возвращаются на Землю
        for cosmonaut in self._cosmonauts.list_all(rocket_id=rocket_id):
            self._cosmonauts.set_location(
                cosmonaut.id, in_space=False, station_id=None, rocket_id=None
            )
        return self.find(rocket_id)

    def position(self, rocket_id: int, at: datetime | None = None) -> OrbitPosition:
        rocket = self.find(rocket_id)
        if rocket.orbit is None:
            raise ConflictError(f"Ракета #{rocket_id} не на орбите (статус: {rocket.status})")
        return position_of(rocket.orbit, at)

    def _checked_transition(self, rocket_id: int, target: RocketStatus) -> Rocket:
        rocket = self.find(rocket_id)
        if target not in _ROCKET_TRANSITIONS[rocket.status]:
            raise ConflictError(
                f"Переход {rocket.status} -> {target} невозможен: "
                "ракета непереиспользуемая, порядок статусов фиксирован"
            )
        return rocket

    def _board_crew(self, rocket: Rocket) -> None:
        """Экипаж взятой миссии садится в ракету при запуске."""
        if rocket.mission_id is None:
            return
        for cosmonaut in self._cosmonauts.list_all(rocket_id=rocket.id):
            self._cosmonauts.set_location(
                cosmonaut.id, in_space=True, station_id=None, rocket_id=rocket.id
            )


class MissionService:
    def __init__(
        self, missions: MissionRepo, rockets: RocketRepo,
        cosmonauts: CosmonautRepo, resources: ResourceRepo,
    ) -> None:
        self._missions = missions
        self._rockets = rockets
        self._cosmonauts = cosmonauts
        self._resources = resources

    def post(self, data: MissionCreate) -> Mission:
        return self._missions.add(data)

    def find(self, mission_id: int) -> Mission:
        mission = self._missions.get(mission_id)
        if mission is None:
            raise NotFoundError("Миссия", mission_id)
        return mission

    def board(self, status: MissionStatus | None = None) -> list[Mission]:
        return self._missions.list_all(status)

    def take(self, mission_id: int, rocket_id: int, crew_ids: list[int]) -> Mission:
        mission = self._transition_checked(mission_id, MissionStatus.TAKEN)
        rocket = self._rockets.get(rocket_id)
        if rocket is None:
            raise NotFoundError("Ракета", rocket_id)
        if rocket.status is not RocketStatus.CREATED:
            raise ConflictError(f"Ракета #{rocket_id} уже использована (статус: {rocket.status})")
        if rocket.mission_id is not None:
            raise ConflictError(f"Ракета #{rocket_id} уже занята миссией #{rocket.mission_id}")

        if crew_ids:
            if rocket.type.kind is not RocketKind.PASSENGER:
                raise ConflictError("Экипаж можно перевозить только пассажирской ракетой")
            if len(crew_ids) > rocket.type.capacity:
                raise ConflictError(
                    f"Мест в «{rocket.type.name}»: {rocket.type.capacity:g}, экипаж: {len(crew_ids)}"
                )
            for cosmonaut_id in crew_ids:
                cosmonaut = self._cosmonauts.get(cosmonaut_id)
                if cosmonaut is None:
                    raise NotFoundError("Космонавт", cosmonaut_id)
                if cosmonaut.in_space or cosmonaut.rocket_id is not None:
                    raise ConflictError(f"Космонавт #{cosmonaut_id} недоступен — уже в полёте")
        elif mission.cargo_tons > 0:
            if rocket.type.kind is not RocketKind.CARGO:
                raise ConflictError("Груз можно перевозить только грузовой ракетой")
            if mission.cargo_tons > rocket.type.capacity:
                raise ConflictError(
                    f"Грузоподъёмность «{rocket.type.name}»: {rocket.type.capacity:g} т, "
                    f"нужно: {mission.cargo_tons:g} т"
                )

        self._missions.assign(mission_id, rocket_id, crew_ids)
        for cosmonaut_id in crew_ids:
            self._cosmonauts.set_location(
                cosmonaut_id, in_space=False, station_id=None, rocket_id=rocket_id
            )
        self._missions.set_status(mission_id, MissionStatus.TAKEN)
        return self.find(mission_id)

    def complete(self, mission_id: int) -> Mission:
        mission = self._transition_checked(mission_id, MissionStatus.DONE)
        if mission.rocket_id is not None:
            rocket = self._rockets.get(mission.rocket_id)
            if rocket is not None and rocket.status in (RocketStatus.CREATED, RocketStatus.FLYING):
                raise ConflictError(
                    f"Ракета миссии ещё не долетела (статус: {rocket.status}) — "
                    "сначала пристыкуйтесь или приземлитесь"
                )
        self._missions.set_status(mission_id, MissionStatus.DONE)
        self._resources.deposit(CREDITS, mission.reward)
        return self.find(mission_id)

    def cancel(self, mission_id: int) -> Mission:
        self._transition_checked(mission_id, MissionStatus.CANCELLED)
        self._release_crew(mission_id)
        self._missions.set_status(mission_id, MissionStatus.CANCELLED)
        return self.find(mission_id)

    def move(self, mission_id: int, target: MissionStatus) -> Mission:
        """Перетаскивание по канбану: диспетчеризация в доменные операции."""
        match target:
            case MissionStatus.DONE:
                return self.complete(mission_id)
            case MissionStatus.CANCELLED:
                return self.cancel(mission_id)
            case MissionStatus.OPEN:
                self._transition_checked(mission_id, MissionStatus.OPEN)
                self._release_crew(mission_id)
                self._missions.assign(mission_id, None, [])
                self._missions.set_status(mission_id, MissionStatus.OPEN)
                return self.find(mission_id)
            case MissionStatus.TAKEN:
                raise ConflictError(
                    "Чтобы взять миссию, назначьте ракету и экипаж: POST /missions/{id}/take"
                )

    def _release_crew(self, mission_id: int) -> None:
        mission = self.find(mission_id)
        for cosmonaut in mission.crew:
            if not cosmonaut.in_space and cosmonaut.station_id is None:
                self._cosmonauts.set_location(
                    cosmonaut.id, in_space=False, station_id=None, rocket_id=None
                )

    def _transition_checked(self, mission_id: int, target: MissionStatus) -> Mission:
        mission = self.find(mission_id)
        if target not in _MISSION_TRANSITIONS[mission.status]:
            raise ConflictError(f"Переход миссии {mission.status} -> {target} невозможен")
        return mission


class MapService:
    """Агрегат для страницы «Земля»: все объекты на орбитах с координатами."""

    def __init__(self, stations: StationRepo, rockets: RocketRepo) -> None:
        self._stations = stations
        self._rockets = rockets

    def world(self, at: datetime | None = None) -> WorldMap:
        at = at or _now()
        stations = [
            StationOnMap(**s.model_dump(), position=position_of(s.orbit, at))
            for s in self._stations.list_all()
        ]
        rockets = [
            RocketOnMap(**r.model_dump(), position=position_of(r.orbit, at))
            for r in self._rockets.list_all()
            if r.orbit is not None
        ]
        return WorldMap(at=at, stations=stations, rockets=rockets)
