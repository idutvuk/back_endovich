"""CORE — доменные модели. Не знают ни про HTTP, ни про SQL."""

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.core.orbits import EARTH_RADIUS_KM


class RocketKind(StrEnum):
    CARGO = "cargo"
    PASSENGER = "passenger"


class RocketStatus(StrEnum):
    CREATED = "created"
    FLYING = "flying"
    DOCKED = "docked"
    DESCENDING = "descending"
    LANDED = "landed"


class MissionStatus(StrEnum):
    OPEN = "open"
    TAKEN = "taken"
    DONE = "done"
    CANCELLED = "cancelled"


class Orbit(BaseModel):
    """Круговая орбита: радиуса и фазы на момент эпохи достаточно,
    чтобы в любой момент времени рассчитать точные координаты."""

    radius_km: float = Field(gt=EARTH_RADIUS_KM)
    phase_deg: float = Field(ge=0, lt=360, default=0)
    epoch: datetime


class OrbitPosition(BaseModel):
    at: datetime
    radius_km: float
    angle_deg: float
    x_km: float
    y_km: float
    period_min: float


# --- Космонавты ---


class CosmonautCreate(BaseModel):
    name: str = Field(min_length=1)
    country: str = Field(min_length=1)
    birth_date: date


class Cosmonaut(CosmonautCreate):
    id: int
    zodiac: str
    in_space: bool = False
    station_id: int | None = None
    rocket_id: int | None = None


# --- Станции ---


class StationCreate(BaseModel):
    name: str = Field(min_length=1)
    orbit: Orbit
    oxygen: float = Field(ge=0, le=1, default=1.0)


class Station(StationCreate):
    id: int


# --- Ракеты ---


class RocketTypeCreate(BaseModel):
    code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    kind: RocketKind
    capacity: float = Field(gt=0, description="тонны для грузовой, места для пассажирской")
    cost: dict[str, float] = Field(description="ресурс -> тонны, напр. {'говно': 2, 'палки': 3}")


class RocketType(RocketTypeCreate):
    id: int


class Rocket(BaseModel):
    id: int
    name: str
    type: RocketType
    status: RocketStatus
    station_id: int | None = None
    mission_id: int | None = None
    orbit: Orbit | None = None


# --- Миссии ---


class MissionCreate(BaseModel):
    name: str = Field(min_length=1)
    cargo_tons: float = Field(ge=0, default=0)
    reward: int = Field(ge=0)
    starts_at: date | None = None
    deadline: date | None = None
    station_id: int | None = None


class Mission(MissionCreate):
    id: int
    status: MissionStatus = MissionStatus.OPEN
    rocket_id: int | None = None
    crew: list[Cosmonaut] = []


# --- Ресурсы ---


class Resource(BaseModel):
    name: str
    amount: float = Field(ge=0)


# --- Карта (агрегат для фронта) ---


class StationOnMap(Station):
    position: OrbitPosition


class RocketOnMap(Rocket):
    position: OrbitPosition


class WorldMap(BaseModel):
    at: datetime
    earth_radius_km: float = EARTH_RADIUS_KM
    stations: list[StationOnMap]
    rockets: list[RocketOnMap]
