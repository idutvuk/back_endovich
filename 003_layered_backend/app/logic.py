"""LOGIC — классы, которые делают бизнес-логику.

Не знает ни про HTTP, ни про SQL: сверху View, снизу интерфейс SonRepo.
"""

from app.repo import SonRepo
from app.schemas import Son, SonCreate


class SonNotFoundError(Exception):
    pass


class SonService:
    def __init__(self, repo: SonRepo) -> None:
        self._repo = repo

    def register_son(self, data: SonCreate) -> Son:
        # Бизнес-правило: имя храним нормализованным.
        normalized = data.model_copy(update={"name": data.name.strip().title()})
        return self._repo.add(normalized)

    def find_son(self, son_id: int) -> Son:
        son = self._repo.get(son_id)
        if son is None:
            raise SonNotFoundError(f"Сын #{son_id} не найден")
        return son

    def all_sons(self) -> list[Son]:
        return self._repo.list_all()

    def expel_son(self, son_id: int) -> None:
        if not self._repo.delete(son_id):
            raise SonNotFoundError(f"Сын #{son_id} не найден")
