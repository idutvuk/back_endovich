"""VIEW — HTTP для станций: список, точные координаты в момент запроса, кислород."""

from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.models import OrbitPosition, Station, StationCreate
from app.views.deps import StationsDep

router = APIRouter(prefix="/stations", tags=["stations"])


class OxygenUpdate(BaseModel):
    oxygen: float = Field(ge=0, le=1)


@router.get("")
def list_stations(service: StationsDep) -> list[Station]:
    return service.list_all()


@router.post("", status_code=status.HTTP_201_CREATED)
def build_station(data: StationCreate, service: StationsDep) -> Station:
    return service.build(data)


@router.get("/{station_id}")
def get_station(station_id: int, service: StationsDep) -> Station:
    return service.find(station_id)


@router.get("/{station_id}/position")
def station_position(
    station_id: int, service: StationsDep, at: datetime | None = None
) -> OrbitPosition:
    return service.position(station_id, at)


@router.patch("/{station_id}/oxygen")
def set_oxygen(station_id: int, data: OxygenUpdate, service: StationsDep) -> Station:
    return service.set_oxygen(station_id, data.oxygen)
