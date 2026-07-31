"""Схемы (DTO) — форма данных, которые ходят между слоями и наружу по REST API."""

from pydantic import BaseModel, Field


class SonCreate(BaseModel):
    """То, что присылает фронт при создании."""

    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)


class Son(BaseModel):
    """То, что возвращаем наружу (уже с id из базы)."""

    id: int
    name: str
    age: int
