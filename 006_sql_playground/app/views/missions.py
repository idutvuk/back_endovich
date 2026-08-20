from fastapi import APIRouter, Depends, HTTPException, status

from app.models import Mission, MissionCreate, MissionDetail
from app.services import BureauService, ConflictError, NotFoundError
from app.views.deps import get_service

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("", status_code=status.HTTP_201_CREATED)
def plan(
    data: MissionCreate,
    service: BureauService = Depends(get_service),
) -> Mission:
    return service.plan_mission(data)


@router.get("")
def list_missions(service: BureauService = Depends(get_service)) -> list[Mission]:
    return service.missions()


@router.get("/{mission_id}")
def get_mission(
    mission_id: int,
    service: BureauService = Depends(get_service),
) -> MissionDetail:
    """Миссия вместе с экипажем."""
    try:
        return service.find_mission(mission_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/{mission_id}/crew/{cosmonaut_id}")
def assign(
    mission_id: int,
    cosmonaut_id: int,
    service: BureauService = Depends(get_service),
) -> MissionDetail:
    """Зачислить космонавта в экипаж — создаёт строку в mission_crew."""
    try:
        return service.assign(mission_id, cosmonaut_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete("/{mission_id}/crew/{cosmonaut_id}")
def dismiss(
    mission_id: int,
    cosmonaut_id: int,
    service: BureauService = Depends(get_service),
) -> MissionDetail:
    """Списать из экипажа — удаляет строку из mission_crew."""
    try:
        return service.dismiss(mission_id, cosmonaut_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
