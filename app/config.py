"""
@file config.py
@brief Конфигурация подключения к базе данных и управление сессиями SQLAlchemy.

Модуль загружает переменные окружения из файла `.env`, создаёт
движок SQLAlchemy и предоставляет dependency-функцию для получения
сессии БД в обработчиках FastAPI.
"""

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

## @brief URL подключения к базе данных, полученный из переменной окружения DATABASE_URL.
api_key = os.getenv("DATABASE_URL")
if not api_key:
    raise RuntimeError("DATABASE_URL не задан")

## @brief Глобальный движок SQLAlchemy, созданный на основе DATABASE_URL.
engine = create_engine(api_key)


def get_session():
    """
    @brief Dependency-функция FastAPI для получения сессии БД.

    Открывает сессию SQLAlchemy и гарантированно закрывает её
    после завершения обработки запроса.

    @yield Session Активная сессия SQLAlchemy.
    """
    with Session(engine) as session:
        yield session