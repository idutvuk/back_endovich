"""VIEW — HTTP для склада ресурсов («говно», «палки», «кредиты»)."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.models import Resource
from app.views.deps import ResourcesDep

router = APIRouter(prefix="/resources", tags=["resources"])


class Deposit(BaseModel):
    name: str = Field(min_length=1)
    amount: float = Field(gt=0)


@router.get("")
def list_resources(repo: ResourcesDep) -> list[Resource]:
    return repo.list_all()


@router.post("/deposit")
def deposit(data: Deposit, repo: ResourcesDep) -> Resource:
    return repo.deposit(data.name, data.amount)
