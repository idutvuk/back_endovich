"""VIEWS — функции, которые обрабатывают запросы (декораторы FastAPI).

Знает только HTTP: принял запрос -> дёрнул логику -> вернул ответ.
Ошибки предметной области ловим прямо тут и превращаем в HTTPException.
Никакой бизнес-логики и никакого SQL здесь нет.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import CosmonautNotFoundError, MissionConflictError
from app.core.models import Cosmonaut, CosmonautCreate
from app.core.services import CosmonautService, MissionService
from app.views.deps import get_cosmonaut_service, get_mission_service

router = APIRouter(prefix="/cosmonauts", tags=["cosmonauts"])


@router.post("", status_code=status.HTTP_201_CREATED)
def enroll(
    data: CosmonautCreate,
    service: CosmonautService = Depends(get_cosmonaut_service),
) -> Cosmonaut:
    return service.enroll(data)


@router.get("")
def roster(
    in_space: bool | None = None,
    service: CosmonautService = Depends(get_cosmonaut_service),
) -> list[Cosmonaut]:
    """GET /cosmonauts?in_space=true — фильтр по тем, кто на орбите."""
    return service.roster(in_space)


@router.get("/{cosmonaut_id}")
def get_cosmonaut(
    cosmonaut_id: int,
    service: CosmonautService = Depends(get_cosmonaut_service),
) -> Cosmonaut:
    try:
        return service.find(cosmonaut_id)
    except CosmonautNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{cosmonaut_id}", status_code=status.HTTP_204_NO_CONTENT)
def expel(
    cosmonaut_id: int,
    service: CosmonautService = Depends(get_cosmonaut_service),
) -> None:
    try:
        service.expel(cosmonaut_id)
    except CosmonautNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    except MissionConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/{cosmonaut_id}/launch")
def launch(
    cosmonaut_id: int,
    service: MissionService = Depends(get_mission_service),
) -> Cosmonaut:
    try:
        return service.launch(cosmonaut_id)
    except CosmonautNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    except MissionConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/{cosmonaut_id}/land")
def land(
    cosmonaut_id: int,
    service: MissionService = Depends(get_mission_service),
) -> Cosmonaut:
    try:
        return service.land(cosmonaut_id)
    except CosmonautNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    except MissionConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/{cosmonaut_id}/age_change")
def age_change(
    cosmonaut_id: int,
    new_age: int,
    service: CosmonautService = Depends(get_cosmonaut_service),
) -> Cosmonaut:
    try:
        return service.age_change(cosmonaut_id, new_age)
    except CosmonautNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))