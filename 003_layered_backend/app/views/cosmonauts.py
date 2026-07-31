"""VIEWS — классы, которые обрабатывают запросы.

Знает только HTTP: принял запрос -> дёрнул логику -> вернул ответ.
Никакой бизнес-логики и никакого SQL здесь нет.
"""

from fastapi import APIRouter, status

from app.core.models import Cosmonaut, CosmonautCreate
from app.core.services import CosmonautService, MissionService


class CosmonautViews:
    def __init__(
        self, cosmonauts: CosmonautService, missions: MissionService
    ) -> None:
        self._cosmonauts = cosmonauts
        self._missions = missions
        self.router = APIRouter(prefix="/cosmonauts", tags=["cosmonauts"])
        # Те самые декораторы FastAPI, применённые к методам класса.
        self.router.post("", status_code=status.HTTP_201_CREATED)(self.enroll)
        self.router.get("")(self.roster)
        self.router.get("/{cosmonaut_id}")(self.get_cosmonaut)
        self.router.delete("/{cosmonaut_id}", status_code=status.HTTP_204_NO_CONTENT)(
            self.expel
        )
        self.router.post("/{cosmonaut_id}/launch")(self.launch)
        self.router.post("/{cosmonaut_id}/land")(self.land)

    def enroll(self, data: CosmonautCreate) -> Cosmonaut:
        return self._cosmonauts.enroll(data)

    def roster(self, in_space: bool | None = None) -> list[Cosmonaut]:
        """GET /cosmonauts?in_space=true — фильтр по тем, кто на орбите."""
        return self._cosmonauts.roster(in_space)

    def get_cosmonaut(self, cosmonaut_id: int) -> Cosmonaut:
        return self._cosmonauts.find(cosmonaut_id)

    def expel(self, cosmonaut_id: int) -> None:
        self._cosmonauts.expel(cosmonaut_id)

    def launch(self, cosmonaut_id: int) -> Cosmonaut:
        return self._missions.launch(cosmonaut_id)

    def land(self, cosmonaut_id: int) -> Cosmonaut:
        return self._missions.land(cosmonaut_id)
