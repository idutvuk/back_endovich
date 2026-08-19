"""CORE (LOGIC) — классы, которые делают бизнес-логику.

Не знает ни про HTTP, ни про SQL: сверху views, снизу интерфейс CosmonautRepo.
"""

from app.core.exceptions import CosmonautNotFoundError, MissionConflictError
from app.core.interfaces import CosmonautRepo
from app.core.models import Cosmonaut, CosmonautCreate
from app.views import cosmonauts


class CosmonautService:
    def __init__(self, repo: CosmonautRepo) -> None:
        self._repo = repo

    def enroll(self, data: CosmonautCreate) -> Cosmonaut:
        # Бизнес-правило: имя храним нормализованным.
        if data.month == 1 or data.month == 2:
            data.Zodiac = "лох"
        elif data.month == 3 and data.date < 15:
            data.Zodiac = "лох"
        else:
            data.Zodiac = "крутой"

        normalized = data.model_copy(update={"name": data.name.strip().title()})
        return self._repo.add(normalized)

    def find(self, cosmonaut_id: int) -> Cosmonaut:
        cosmonaut = self._repo.get(cosmonaut_id)
        if cosmonaut is None:
            raise CosmonautNotFoundError(cosmonaut_id)
        return cosmonaut

    def roster(self, in_space: bool | None = None) -> list[Cosmonaut]:
        return self._repo.list_all(in_space)

    def expel(self, cosmonaut_id: int) -> None:
        # Бизнес-правило: нельзя отчислить того, кто сейчас на орбите.
        if self.find(cosmonaut_id).in_space:
            raise MissionConflictError(
                f"Космонавт #{cosmonaut_id} на орбите — сначала верните его"
            )
        self._repo.delete(cosmonaut_id)

    def age_change(self, cosmonaut_id: int,cosmonaut_age: int) -> Cosmonaut:
        cosmonaut = self._get(cosmonaut_id)

        self._repo.set_age(cosmonaut_id,cosmonaut_age)
        return cosmonaut.model_copy(update={"age": cosmonaut_age })

    def _get(self, cosmonaut_id: int) -> Cosmonaut:
        cosmonaut = self._repo.get(cosmonaut_id)
        if cosmonaut is None:
            raise CosmonautNotFoundError(cosmonaut_id)
        return cosmonaut


class MissionService:
    """Запуск и возвращение. Отдельный класс: другая зона ответственности."""

    def __init__(self, repo: CosmonautRepo) -> None:
        self._repo = repo

    def launch(self, cosmonaut_id: int) -> Cosmonaut:
        cosmonaut = self._get(cosmonaut_id)
        if cosmonaut.in_space:
            raise MissionConflictError(f"Космонавт #{cosmonaut_id} уже в космосе")
        self._repo.set_in_space(cosmonaut_id, True)
        return cosmonaut.model_copy(update={"in_space": True})

    def land(self, cosmonaut_id: int) -> Cosmonaut:
        cosmonaut = self._get(cosmonaut_id)
        if not cosmonaut.in_space:
            raise MissionConflictError(f"Космонавт #{cosmonaut_id} и так на Земле")
        self._repo.set_in_space(cosmonaut_id, False)
        return cosmonaut.model_copy(update={"in_space": False})

    def _get(self, cosmonaut_id: int) -> Cosmonaut:
        cosmonaut = self._repo.get(cosmonaut_id)
        if cosmonaut is None:
            raise CosmonautNotFoundError(cosmonaut_id)
        return cosmonaut