from sqlalchemy import Column, ForeignKey, Table, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

DB_URL = "sqlite:///bureau.sqlite3"


class Base(DeclarativeBase):
    pass


# Таблица-связка. Своих данных не несёт, поэтому это просто Table,
# а не класс: две колонки, обе — внешние ключи, вместе — составной PK.
mission_crew = Table(
    "mission_crew",
    Base.metadata,
    Column("mission_id", ForeignKey("missions.id"), primary_key=True),
    Column("cosmonaut_id", ForeignKey("cosmonauts.id"), primary_key=True),
)


class CosmonautRow(Base):
    __tablename__ = "cosmonauts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    in_space: Mapped[bool] = mapped_column(default=False)

    missions: Mapped[list["MissionRow"]] = relationship(
        secondary=mission_crew, back_populates="crew"
    )


class MissionRow(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    destination: Mapped[str]
    year: Mapped[int]

    crew: Mapped[list[CosmonautRow]] = relationship(
        secondary=mission_crew, back_populates="missions"
    )


engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def create_tables() -> None:
    Base.metadata.create_all(engine)


def seed() -> None:
    """Стартовые данные, чтобы в /sql сразу было что поджойнить."""
    with SessionLocal() as session:
        if session.scalars(select(CosmonautRow)).first() is not None:
            return  # база уже обжита

        gagarin = CosmonautRow(name="Юрий Гагарин", age=27)
        tereshkova = CosmonautRow(name="Валентина Терешкова", age=26)
        leonov = CosmonautRow(name="Алексей Леонов", age=30)
        belyaev = CosmonautRow(name="Павел Беляев", age=40)

        session.add_all(
            [
                MissionRow(
                    name="Восток-1",
                    destination="Орбита Земли",
                    year=1961,
                    crew=[gagarin],
                ),
                MissionRow(
                    name="Восток-6",
                    destination="Орбита Земли",
                    year=1963,
                    crew=[tereshkova],
                ),
                MissionRow(
                    name="Восход-2",
                    destination="Открытый космос",
                    year=1965,
                    crew=[leonov, belyaev],
                ),
                MissionRow(
                    name="Союз-19",
                    destination="Стыковка с Аполлоном",
                    year=1975,
                    crew=[leonov],
                ),
            ]
        )
        session.commit()
