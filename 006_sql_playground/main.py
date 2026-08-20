from fastapi import FastAPI

from app.db import create_tables, seed
from app.views import cosmonauts, missions, sql

create_tables()
seed()

app = FastAPI(title="006 SQL Playground")
app.include_router(sql.router)
app.include_router(cosmonauts.router)
app.include_router(missions.router)
