"""Демо-данные бюро: станции, космонавты, типы ракет, ресурсы, миссии.

Заполняет базу только если она пуста.
"""

from datetime import UTC, date, datetime

from sqlalchemy import select

from app.core.models import MissionStatus, RocketStatus
from app.repository.db import (
    CosmonautRow,
    MissionRow,
    ResourceRow,
    RocketRow,
    RocketTypeRow,
    SessionLocal,
    StationRow,
)

EPOCH = datetime(2026, 1, 1, tzinfo=UTC).replace(tzinfo=None)


def seed() -> None:
    with SessionLocal() as session:
        if session.scalar(select(StationRow.id)) is not None:
            return

        stations = [
            StationRow(name="«Синс-1»", radius_km=6771, phase_deg=0, epoch=EPOCH, oxygen=0.97),
            StationRow(name="«Заря-М»", radius_km=7071, phase_deg=120, epoch=EPOCH, oxygen=0.82),
            StationRow(name="«Рога-Орбитальная»", radius_km=7571, phase_deg=250, epoch=EPOCH, oxygen=0.64),
        ]
        session.add_all(stations)
        session.flush()

        cosmonauts = [
            CosmonautRow(name="Герман Синс-мл.", country="Россия", birth_date=date(1990, 4, 12),
                         in_space=True, station_id=stations[0].id),
            CosmonautRow(name="Анна Орлова", country="Россия", birth_date=date(1993, 8, 2),
                         in_space=True, station_id=stations[0].id),
            CosmonautRow(name="Джон Крейтер", country="США", birth_date=date(1988, 1, 28),
                         in_space=True, station_id=stations[1].id),
            CosmonautRow(name="Ли Вэй", country="Китай", birth_date=date(1995, 11, 5)),
            CosmonautRow(name="Мария Гонсалес", country="Мексика", birth_date=date(1992, 6, 21)),
            CosmonautRow(name="Пьер Дюбуа", country="Франция", birth_date=date(1985, 12, 25)),
            CosmonautRow(name="Айгерим Нурланова", country="Казахстан", birth_date=date(1997, 3, 8)),
            CosmonautRow(name="Юрий Палкин", country="Россия", birth_date=date(1991, 10, 30)),
        ]
        session.add_all(cosmonauts)

        proton = RocketTypeRow(
            code="proton-gk", name="Протон-ГК", kind="cargo",
            capacity=20, cost={"говно": 2, "палки": 3},
        )
        soyuz = RocketTypeRow(
            code="soyuz-pk", name="Союз-ПК", kind="passenger",
            capacity=3, cost={"говно": 5, "палки": 4},
        )
        session.add_all([proton, soyuz])
        session.flush()

        rockets = [
            RocketRow(name="Протон-ГК", type_id=proton.id, status=RocketStatus.CREATED),
            RocketRow(name="Союз-ПК «Ласточка»", type_id=soyuz.id, status=RocketStatus.DOCKED,
                      station_id=stations[1].id, radius_km=7071, phase_deg=120, epoch=EPOCH),
            RocketRow(name="Протон-ГК «Трудяга»", type_id=proton.id, status=RocketStatus.FLYING,
                      station_id=stations[2].id, radius_km=7371, phase_deg=220, epoch=EPOCH),
            RocketRow(name="Союз-ПК «Ветеран»", type_id=soyuz.id, status=RocketStatus.LANDED),
        ]
        session.add_all(rockets)
        session.flush()

        session.add_all([
            ResourceRow(name="говно", amount=42),
            ResourceRow(name="палки", amount=37),
            ResourceRow(name="кредиты", amount=1000),
        ])

        session.add_all([
            MissionRow(name="Доставка кислородных баллонов", status=MissionStatus.OPEN,
                       cargo_tons=8, reward=500, starts_at=date(2026, 8, 10),
                       deadline=date(2026, 9, 1), station_id=stations[2].id),
            MissionRow(name="Ротация экипажа «Синс-1»", status=MissionStatus.OPEN,
                       cargo_tons=0, reward=800, starts_at=date(2026, 8, 15),
                       deadline=date(2026, 10, 1), station_id=stations[0].id),
            MissionRow(name="Вывоз мусора с «Зари-М»", status=MissionStatus.TAKEN,
                       cargo_tons=12, reward=300, rocket_id=rockets[2].id,
                       station_id=stations[1].id, deadline=date(2026, 8, 20)),
            MissionRow(name="Юбилейный салют бюро", status=MissionStatus.DONE,
                       cargo_tons=1, reward=100),
            MissionRow(name="Экспедиция на Луну", status=MissionStatus.CANCELLED,
                       cargo_tons=0, reward=9000),
        ])

        session.commit()
