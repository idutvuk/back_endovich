"""Контракты, от которых зависит логика.

Интерфейс репозитория живёт в core, а не в repository, — это инверсия
зависимостей: ядро диктует контракт, реализация подстраивается.
"""

from typing import Protocol

from app.core.models import Cosmonaut, CosmonautCreate


class CosmonautRepo(Protocol):
    """Интерфейс репозитория. Логика зависит от него, а не от sqlite."""

    def add(self, cosmonaut: CosmonautCreate) -> Cosmonaut: ...

    def get(self, cosmonaut_id: int) -> Cosmonaut | None: ...

    def list_all(self, in_space: bool | None = None) -> list[Cosmonaut]: ...

    def set_in_space(self, cosmonaut_id: int, in_space: bool) -> None: ...

    def set_name(self, cosmonaut_id: int, new_name: str) -> None: ...

    def delete(self, cosmonaut_id: int) -> bool: ...
