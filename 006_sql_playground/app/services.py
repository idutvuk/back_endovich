from app.models import (
    Cosmonaut,
    CosmonautCreate,
    CosmonautDetail,
    Mission,
    MissionCreate,
    MissionDetail,
)
from app.repository import CosmonautRepo, MissionRepo

CREW_LIMIT = 3  # капсула трёхместная


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class BureauService:
    def __init__(self, cosmonauts: CosmonautRepo, missions: MissionRepo) -> None:
        self._cosmonauts = cosmonauts
        self._missions = missions

    # --- космонавты ---

    def enroll(self, data: CosmonautCreate) -> Cosmonaut:
        normalized = data.model_copy(update={"name": data.name.strip().title()})
        return self._cosmonauts.add(normalized)

    def find_cosmonaut(self, cosmonaut_id: int) -> CosmonautDetail:
        cosmonaut = self._cosmonauts.get(cosmonaut_id)
        if cosmonaut is None:
            raise NotFoundError(f"Космонавт #{cosmonaut_id} не найден")
        return cosmonaut

    def roster(self) -> list[Cosmonaut]:
        return self._cosmonauts.list_all()

    # --- миссии ---

    def plan_mission(self, data: MissionCreate) -> Mission:
        return self._missions.add(data)

    def find_mission(self, mission_id: int) -> MissionDetail:
        mission = self._missions.get(mission_id)
        if mission is None:
            raise NotFoundError(f"Миссия #{mission_id} не найдена")
        return mission

    def missions(self) -> list[Mission]:
        return self._missions.list_all()

    # --- экипаж (many-to-many) ---

    def assign(self, mission_id: int, cosmonaut_id: int) -> MissionDetail:
        self.find_mission(mission_id)
        self.find_cosmonaut(cosmonaut_id)
        crew = self._missions.crew_ids(mission_id)
        if cosmonaut_id in crew:
            raise ConflictError(f"Космонавт #{cosmonaut_id} уже в экипаже")
        if len(crew) >= CREW_LIMIT:
            raise ConflictError(f"Экипаж полон: максимум {CREW_LIMIT} места")
        self._missions.assign(mission_id, cosmonaut_id)
        return self.find_mission(mission_id)

    def dismiss(self, mission_id: int, cosmonaut_id: int) -> MissionDetail:
        self.find_mission(mission_id)
        if cosmonaut_id not in self._missions.crew_ids(mission_id):
            raise NotFoundError(f"Космонавта #{cosmonaut_id} нет в экипаже")
        self._missions.dismiss(mission_id, cosmonaut_id)
        return self.find_mission(mission_id)
