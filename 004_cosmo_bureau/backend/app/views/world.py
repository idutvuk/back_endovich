"""VIEW — агрегат для страницы «Земля»: все объекты с координатами в момент запроса."""

from datetime import datetime

from fastapi import APIRouter

from app.core.models import WorldMap
from app.views.deps import MapDep

router = APIRouter(prefix="/map", tags=["map"])


@router.get("")
def world_map(service: MapDep, at: datetime | None = None) -> WorldMap:
    return service.world(at)
