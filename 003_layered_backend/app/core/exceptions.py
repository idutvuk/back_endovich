"""Ошибки предметной области.

Логика бросает их, ничего не зная про HTTP.
В HTTP-статусы их превращает слой views (views/errors.py).
"""


class DomainError(Exception):
    """Базовая ошибка предметной области."""


class CosmonautNotFoundError(DomainError):
    def __init__(self, cosmonaut_id: int) -> None:
        super().__init__(f"Космонавт #{cosmonaut_id} не найден")

class InvalidCosmonautAge(DomainError): ...


class MissionConflictError(DomainError):
    """Действие противоречит текущему состоянию космонавта."""
