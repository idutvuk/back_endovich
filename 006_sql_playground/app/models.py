from typing import Any

from pydantic import BaseModel, Field


class CosmonautCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=18, le=100)


class Cosmonaut(BaseModel):
    id: int
    name: str
    age: int
    in_space: bool = False


class MissionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    destination: str = Field(min_length=1, max_length=200)
    year: int = Field(ge=1957)  # раньше 1957 не летали


class Mission(BaseModel):
    id: int
    name: str
    destination: str
    year: int


class MissionDetail(Mission):
    crew: list[Cosmonaut]


class CosmonautDetail(Cosmonaut):
    missions: list[Mission]


class SqlQuery(BaseModel):
    query: str = Field(min_length=1, description="Любой SQL одним стейтментом")


class SqlResult(BaseModel):
    columns: list[str] | None = None
    rows: list[list[Any]] | None = None
    rowcount: int | None = None
