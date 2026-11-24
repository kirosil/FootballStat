"""
@file schemas.py
@brief Pydantic-схемы запросов API.

Описывают структуру JSON, принимаемого эндпоинтами статистики.
"""

from pydantic import BaseModel
from typing import List


## @brief Параметры запроса агрегированной статистики одной команды.
class Team(BaseModel):
    ## @brief Идентификатор команды.
    team_id: int
    ## @brief Количество последних матчей для анализа.
    matches_count: int
    ## @brief Место игры: 1 — дома, 2 — в гостях, 3 — все.
    where_played: int
    ## @brief Тип агрегации: 1 — среднее, 2 — минимум, 3 — максимум.
    how_show: int
    ## @brief Список метрик для расчёта.
    stats: List[str]


## @brief Параметры запроса тренда одной метрики команды.
class TeamTrend(BaseModel):
    ## @brief Идентификатор команды.
    team_id: int
    ## @brief Количество последних матчей.
    matches_count: int
    ## @brief Место игры: 1 — дома, 2 — в гостях, 3 — все.
    where_played: int
    ## @brief Название метрики (одна).
    stats: str