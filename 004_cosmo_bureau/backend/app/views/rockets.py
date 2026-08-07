"""VIEW — HTTP для ракет: типы, постройка за ресурсы, жизненный цикл."""

from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.models import OrbitPosition, Rocket, RocketStatus, RocketType, RocketTypeCreate
from app.views.deps import RocketsDep

router = APIRouter(prefix="/rockets", tags=["rockets"])


class BuildRequest(BaseModel):
    type_code: str
    name: str | None = None


class LaunchRequest(BaseModel):
    station_id: int


class DescendRequest(BaseModel):
    crew_ids: list[int] = []


@router.get("/types")
def list_types(service: RocketsDep) -> list[RocketType]:
    return service.list_types()


@router.post("/types", status_code=status.HTTP_201_CREATED)
def add_type(data: RocketTypeCreate, service: RocketsDep) -> RocketType:
    return service.add_type(data)


@router.get("")
def list_rockets(service: RocketsDep, status: RocketStatus | None = None) -> list[Rocket]:
    return service.list_all(status)


@router.post("/build", status_code=status.HTTP_201_CREATED)
def build_rocket(data: BuildRequest, service: RocketsDep) -> Rocket:
    return service.build(data.type_code, data.name)


@router.get("/{rocket_id}")
def get_rocket(rocket_id: int, service: RocketsDep) -> Rocket:
    return service.find(rocket_id)


@router.get("/{rocket_id}/position")
def rocket_position(
    rocket_id: int, service: RocketsDep, at: datetime | None = None
) -> OrbitPosition:
    return service.position(rocket_id, at)


@router.post("/{rocket_id}/launch")
def launch(rocket_id: int, data: LaunchRequest, service: RocketsDep) -> Rocket:
    return service.launch(rocket_id, data.station_id)


@router.post("/{rocket_id}/dock")
def dock(rocket_id: int, service: RocketsDep) -> Rocket:
    return service.dock(rocket_id)


@router.post("/{rocket_id}/descend")
def descend(rocket_id: int, service: RocketsDep, data: DescendRequest | None = None) -> Rocket:
    return service.descend(rocket_id, data.crew_ids if data else [])


@router.post("/{rocket_id}/land")
def land(rocket_id: int, service: RocketsDep) -> Rocket:
    return service.land(rocket_id)
