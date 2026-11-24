"""
@file main.py
@brief Точка входа приложения FastAPI.

Создаёт экземпляр приложения, подключает роутеры и монтирует
статику.
"""

from fastapi import FastAPI
from app.routers import stats, teams
from fastapi.staticfiles import StaticFiles

## @brief Экземпляр приложения FastAPI.
app = FastAPI()

app.include_router(stats.router)
app.include_router(teams.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


