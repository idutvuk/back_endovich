"""VIEWS — функции, которые обрабатывают запросы (декораторы FastAPI).

Знает только HTTP: принял запрос -> дёрнул логику -> вернул ответ.
Ошибки предметной области ловим прямо тут и превращаем в HTTPException.
Никакой бизнес-логики и никакого SQL здесь нет.
"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.exceptions import CosmonautNotFoundError, MissionConflictError
from app.core.models import Cosmonaut, CosmonautCreate, CosmonautUpdate
from app.core.services import CosmonautService, MissionService
from app.views.deps import (
    get_cosmonaut_service,
    get_mission_service,
    require_commander,
)

router = APIRouter(prefix="/cosmonauts", tags=["cosmonauts"])


@router.post("", status_code=status.HTTP_201_CREATED)
def enroll(
    data: CosmonautCreate,
    service: CosmonautService = Depends(get_cosmonaut_service),
) -> Cosmonaut:
    return service.enroll(data)


@router.get("", response_model=list[Cosmonaut])
def roster(
    in_space: bool | None = None,
    format: Literal["json", "csv"] = "json",
    service: CosmonautService = Depends(get_cosmonaut_service),
):
    """GET /cosmonauts?in_space=true&format=csv — фильтр и выбор формата."""
    cosmonauts = service.roster(in_space)
    if format == "csv":
        lines = ["id,name,age,in_space"]
        lines += [f"{c.id},{c.name},{c.age},{c.in_space}" for c in cosmonauts]
        return Response("\n".join(lines), media_type="text/csv")
    return cosmonauts


@router.get("/{cosmonaut_id}")
def get_cosmonaut(
    cosmonaut_id: int,
    service: CosmonautService = Depends(get_cosmonaut_service),
) -> Cosmonaut:
    try:
        return service.find(cosmonaut_id)
    except CosmonautNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/{cosmonaut_id}")
def edit_cosmonaut(
    cosmonaut_id: int,
    data: CosmonautUpdate,
    service: CosmonautService = Depends(get_cosmonaut_service),
) -> Cosmonaut:
    try:
        return service.update(cosmonaut_id, data)
    except CosmonautNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    except MissionConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete(
    "/{cosmonaut_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_commander)],
)
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
