"""VIEW — HTTP для миссий: доска (канбан), взятие, выполнение, отмена."""

from fastapi import APIRouter, status

from app.core.models import Mission, MissionCreate, MissionStatus
from app.views.deps import MissionsDep
from pydantic import BaseModel

router = APIRouter(prefix="/missions", tags=["missions"])


class TakeRequest(BaseModel):
    rocket_id: int
    crew_ids: list[int] = []


class MoveRequest(BaseModel):
    status: MissionStatus


@router.get("")
def list_missions(service: MissionsDep, status: MissionStatus | None = None) -> list[Mission]:
    return service.board(status)


@router.post("", status_code=status.HTTP_201_CREATED)
def post_mission(data: MissionCreate, service: MissionsDep) -> Mission:
    return service.post(data)


@router.get("/{mission_id}")
def get_mission(mission_id: int, service: MissionsDep) -> Mission:
    return service.find(mission_id)


@router.post("/{mission_id}/take")
def take_mission(mission_id: int, data: TakeRequest, service: MissionsDep) -> Mission:
    return service.take(mission_id, data.rocket_id, data.crew_ids)


@router.post("/{mission_id}/complete")
def complete_mission(mission_id: int, service: MissionsDep) -> Mission:
    return service.complete(mission_id)


@router.post("/{mission_id}/cancel")
def cancel_mission(mission_id: int, service: MissionsDep) -> Mission:
    return service.cancel(mission_id)


@router.patch("/{mission_id}/status")
def move_mission(mission_id: int, data: MoveRequest, service: MissionsDep) -> Mission:
    """Для перетаскивания карточки по канбану."""
    return service.move(mission_id, data.status)
