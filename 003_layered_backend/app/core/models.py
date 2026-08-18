"""Модели предметной области (DTO) — ходят между слоями и наружу по REST API."""

from pydantic import BaseModel, Field


class CosmonautCreate(BaseModel):
    """То, что присылает фронт при зачислении в отряд."""

    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=18, le=100)
    sex: str = Field(min_length=1, max_length=100)


class Cosmonaut(BaseModel):
    """То, что возвращаем наружу (уже с id из базы)."""

    id: int
    name: str
    age: int
    in_space: bool = False
    sex: str

