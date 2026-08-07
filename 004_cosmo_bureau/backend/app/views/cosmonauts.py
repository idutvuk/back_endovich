"""VIEW — HTTP для космонавтов: список с поиском по параметрам, CRUD."""

from fastapi import APIRouter, status

from app.core.models import Cosmonaut, CosmonautCreate
from app.views.deps import CosmonautsDep

router = APIRouter(prefix="/cosmonauts", tags=["cosmonauts"])


@router.get("")
def list_cosmonauts(
    service: CosmonautsDep,
    name: str | None = None,
    country: str | None = None,
    in_space: bool | None = None,
    station_id: int | None = None,
    zodiac: str | None = None,
) -> list[Cosmonaut]:
    roster = service.roster(
        name=name, country=country, in_space=in_space, station_id=station_id
    )
    if zodiac:
        roster = [c for c in roster if c.zodiac.lower() == zodiac.lower()]
    return roster


@router.post("", status_code=status.HTTP_201_CREATED)
def enroll_cosmonaut(data: CosmonautCreate, service: CosmonautsDep) -> Cosmonaut:
    return service.enroll(data)


@router.get("/{cosmonaut_id}")
def get_cosmonaut(cosmonaut_id: int, service: CosmonautsDep) -> Cosmonaut:
    return service.find(cosmonaut_id)


@router.delete("/{cosmonaut_id}", status_code=status.HTTP_204_NO_CONTENT)
def expel_cosmonaut(cosmonaut_id: int, service: CosmonautsDep) -> None:
    service.expel(cosmonaut_id)
