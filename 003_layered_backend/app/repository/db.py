"""DB — место, где лежат данные.

Здесь: движок SQLAlchemy, фабрика сессий и ORM-описание таблиц.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DB_URL = "sqlite:///cosmonauts.sqlite3"


class Base(DeclarativeBase):
    pass


class CosmonautRow(Base):
    """Строка таблицы. Не путать с доменной моделью Cosmonaut (pydantic):
    эта — про хранение, та — про предметную область."""

    __tablename__ = "cosmonauts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    in_space: Mapped[bool] = mapped_column(default=False)
    date: Mapped[int]
    month: Mapped[int]
    Zodiac: Mapped[str]


engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def create_tables() -> None:
    Base.metadata.create_all(engine)
