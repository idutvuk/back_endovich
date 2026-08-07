"""Доменные ошибки. Views переводят их в HTTP-статусы."""


class DomainError(Exception):
    """База: любое нарушение бизнес-правил."""


class NotFoundError(DomainError):
    def __init__(self, entity: str, entity_id: int | str) -> None:
        super().__init__(f"{entity} #{entity_id} не найден")


class ConflictError(DomainError):
    """Действие противоречит текущему состоянию (неверный переход статуса и т.п.)."""


class InsufficientResourcesError(DomainError):
    def __init__(self, missing: dict[str, float]) -> None:
        parts = ", ".join(f"{name}: не хватает {amount:g} т" for name, amount in missing.items())
        super().__init__(f"Недостаточно ресурсов — {parts}")
        self.missing = missing
