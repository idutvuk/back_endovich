"""VIEW — классы, которые обрабатывают запросы.

Знает только HTTP: принял запрос -> дёрнул логику -> вернул ответ.
Никакой бизнес-логики и никакого SQL здесь нет.
"""

from fastapi import APIRouter, status

from app.logic import SonService
from app.schemas import Son, SonCreate


class SonViews:
    def __init__(self, service: SonService) -> None:
        self._service = service
        self.router = APIRouter(prefix="/sons", tags=["sons"])
        # Те самые декораторы FastAPI, применённые к методам класса.
        self.router.post("", status_code=status.HTTP_201_CREATED)(self.create_son)
        self.router.get("")(self.list_sons)
        self.router.get("/{son_id}")(self.get_son)
        self.router.delete("/{son_id}", status_code=status.HTTP_204_NO_CONTENT)(
            self.delete_son
        )

    def create_son(self, data: SonCreate) -> Son:
        return self._service.register_son(data)

    def list_sons(self) -> list[Son]:
        return self._service.all_sons()

    def get_son(self, son_id: int) -> Son:
        """Запрос о сыне. Если всё хорошо — ваш сын вернулся 200."""
        return self._service.find_son(son_id)

    def delete_son(self, son_id: int) -> None:
        self._service.expel_son(son_id)
