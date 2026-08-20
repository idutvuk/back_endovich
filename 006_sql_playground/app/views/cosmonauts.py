from fastapi import APIRouter, Depends, HTTPException, status

from app.models import Cosmonaut, CosmonautCreate, CosmonautDetail
from app.services import BureauService, NotFoundError
from app.views.deps import get_service

router = APIRouter(prefix="/cosmonauts", tags=["cosmonauts"])


@router.post("", status_code=status.HTTP_201_CREATED)
def enroll(
    data: CosmonautCreate,
    service: BureauService = Depends(get_service),
) -> Cosmonaut:
    return service.enroll(data)


@router.get("")
def roster(service: BureauService = Depends(get_service)) -> list[Cosmonaut]:
    return service.roster()


@router.get("/{cosmonaut_id}")
def get_cosmonaut(
    cosmonaut_id: int,
    service: BureauService = Depends(get_service),
) -> CosmonautDetail:
    """Космонавт вместе со списком его миссий (many-to-many изнутри)."""
    try:
        return service.find_cosmonaut(cosmonaut_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
