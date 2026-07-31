"""VIEW — классы, которые обрабатывают запросы.

Знает только HTTP: принял запрос -> дёрнул логику -> вернул ответ.
Никакой бизнес-логики и никакого SQL здесь нет.
"""

from fastapi import APIRouter, status

from app.logic import CosmonautService
from app.schemas import Cosmonaut, CosmonautCreate


class CosmonautViews:
    def __init__(self, service: CosmonautService) -> None:
        self._service = service
        self.router = APIRouter(prefix="/cosmonauts", tags=["cosmonauts"])
        # Те самые декораторы FastAPI, применённые к методам класса.
        self.router.post("", status_code=status.HTTP_201_CREATED)(self.enroll)
        self.router.get("")(self.list_cosmonauts)
        self.router.get("/{cosmonaut_id}")(self.get_cosmonaut)
        self.router.delete("/{cosmonaut_id}", status_code=status.HTTP_204_NO_CONTENT)(
            self.expel
        )

    def enroll(self, data: CosmonautCreate) -> Cosmonaut:
        return self._service.enroll(data)

    def list_cosmonauts(self) -> list[Cosmonaut]:
        return self._service.all()

    def get_cosmonaut(self, cosmonaut_id: int) -> Cosmonaut:
        return self._service.find(cosmonaut_id)

    def expel(self, cosmonaut_id: int) -> None:
        self._service.expel(cosmonaut_id)
