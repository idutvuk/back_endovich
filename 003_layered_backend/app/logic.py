"""LOGIC — классы, которые делают бизнес-логику.

Не знает ни про HTTP, ни про SQL: сверху View, снизу интерфейс CosmonautRepo.
"""

from app.repo import CosmonautRepo
from app.schemas import Cosmonaut, CosmonautCreate


class CosmonautNotFoundError(Exception):
    pass


class CosmonautService:
    def __init__(self, repo: CosmonautRepo) -> None:
        self._repo = repo

    def enroll(self, data: CosmonautCreate) -> Cosmonaut:
        # Бизнес-правило: имя храним нормализованным.
        normalized = data.model_copy(update={"name": data.name.strip().title()})
        return self._repo.add(normalized)

    def find(self, cosmonaut_id: int) -> Cosmonaut:
        cosmonaut = self._repo.get(cosmonaut_id)
        if cosmonaut is None:
            raise CosmonautNotFoundError(f"Космонавт #{cosmonaut_id} не найден")
        return cosmonaut

    def all(self) -> list[Cosmonaut]:
        return self._repo.list_all()

    def expel(self, cosmonaut_id: int) -> None:
        if not self._repo.delete(cosmonaut_id):
            raise CosmonautNotFoundError(f"Космонавт #{cosmonaut_id} не найден")
