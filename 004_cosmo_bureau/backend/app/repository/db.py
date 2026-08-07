"""REPOSITORY — подключение к БД и ORM-строки (таблицы)."""

from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

engine = create_engine("sqlite:///cosmo_bureau.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class CosmonautRow(Base):
    __tablename__ = "cosmonauts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    birth_date: Mapped[date] = mapped_column(Date)
    in_space: Mapped[bool] = mapped_column(default=False)
    station_id: Mapped[int | None] = mapped_column(ForeignKey("stations.id"), default=None)
    rocket_id: Mapped[int | None] = mapped_column(ForeignKey("rockets.id"), default=None)


class StationRow(Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    radius_km: Mapped[float] = mapped_column(Float)
    phase_deg: Mapped[float] = mapped_column(Float, default=0)
    epoch: Mapped[datetime] = mapped_column(DateTime)
    oxygen: Mapped[float] = mapped_column(Float, default=1.0)


class RocketTypeRow(Base):
    __tablename__ = "rocket_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String)
    capacity: Mapped[float] = mapped_column(Float)
    cost: Mapped[dict] = mapped_column(JSON)


class RocketRow(Base):
    __tablename__ = "rockets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    type_id: Mapped[int] = mapped_column(ForeignKey("rocket_types.id"))
    status: Mapped[str] = mapped_column(String)
    station_id: Mapped[int | None] = mapped_column(ForeignKey("stations.id"), default=None)
    # Орбита появляется после запуска, поэтому nullable
    radius_km: Mapped[float | None] = mapped_column(Float, default=None)
    phase_deg: Mapped[float | None] = mapped_column(Float, default=None)
    epoch: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    type: Mapped[RocketTypeRow] = relationship(lazy="joined")


class MissionRow(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    cargo_tons: Mapped[float] = mapped_column(Float, default=0)
    reward: Mapped[int] = mapped_column(default=0)
    starts_at: Mapped[date | None] = mapped_column(Date, default=None)
    deadline: Mapped[date | None] = mapped_column(Date, default=None)
    station_id: Mapped[int | None] = mapped_column(ForeignKey("stations.id"), default=None)
    rocket_id: Mapped[int | None] = mapped_column(ForeignKey("rockets.id"), default=None)

    crew: Mapped[list[CosmonautRow]] = relationship(
        secondary="mission_crew", lazy="selectin"
    )


class MissionCrewRow(Base):
    __tablename__ = "mission_crew"

    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), primary_key=True)
    cosmonaut_id: Mapped[int] = mapped_column(ForeignKey("cosmonauts.id"), primary_key=True)


class ResourceRow(Base):
    __tablename__ = "resources"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    amount: Mapped[float] = mapped_column(Float, default=0)


def create_tables() -> None:
    Base.metadata.create_all(engine)
