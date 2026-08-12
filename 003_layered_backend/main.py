"""Точка сборки:

USER -> FRONT -> [ VIEWS -> CORE -> REPOSITORY ] -> DB
                        (этот бэкэнд)

Цепочка DB -> REPO -> LOGIC собирается на каждый запрос
через Depends (см. app/views/deps.py).

Запуск:
    uv run uvicorn main:app --reload
"""

# AAAAAAAAAAAAa

from fastapi import FastAPI

from app.repository.db import create_tables
from app.views.cosmonauts import router

create_tables()

# HelloWorld("print")

app = FastAPI(title="003 Layered Backend — Центр подготовки космонавтов")
app.include_router(router)
