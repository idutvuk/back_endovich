"""Точка сборки. Слои соединяются здесь и только здесь:

USER -> FRONT -> [ VIEWS -> CORE -> REPOSITORY ] -> DB
                        (этот бэкэнд)

Запуск:
    uv run uvicorn main:app --reload
"""

from fastapi import FastAPI

from app.core.services import CosmonautService, MissionService
from app.repository.db import get_connection
from app.repository.sqlite import SqliteCosmonautRepo
from app.views.cosmonauts import CosmonautViews
from app.views.errors import register_error_handlers

# Сборка снизу вверх: DB -> REPOSITORY -> CORE -> VIEWS.
connection = get_connection()
repo = SqliteCosmonautRepo(connection)
cosmonauts = CosmonautService(repo)
missions = MissionService(repo)
views = CosmonautViews(cosmonauts, missions)

app = FastAPI(title="003 Layered Backend — Центр подготовки космонавтов")
app.include_router(views.router)
register_error_handlers(app)
