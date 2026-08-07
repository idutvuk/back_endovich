"""Орбитальная механика: круговые орбиты вокруг Земли.

Период выводится из радиуса по третьему закону Кеплера,
поэтому хранить в БД достаточно радиус, фазу и эпоху.
"""

import math
from datetime import datetime

MU_EARTH_KM3_S2 = 398_600.4418
EARTH_RADIUS_KM = 6_371.0


def orbital_period_s(radius_km: float) -> float:
    return 2 * math.pi * math.sqrt(radius_km**3 / MU_EARTH_KM3_S2)


def angle_at(radius_km: float, phase_deg: float, epoch: datetime, at: datetime) -> float:
    elapsed_s = (at - epoch).total_seconds()
    return (phase_deg + 360.0 * elapsed_s / orbital_period_s(radius_km)) % 360.0
