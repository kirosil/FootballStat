"""
@file models.py
@brief ORM-модели предметной области (SQLModel).

Содержит таблицы: команды, матчи, связь команд с лигами и
пофреймовую статистику матчей.
"""

from sqlmodel import SQLModel, create_engine, Field, Session
from datetime import date

## @brief Таблица футбольных команд.
class teams(SQLModel, table=True):
    ## @brief Уникальный идентификатор команды.
    id: int = Field(primary_key=True)
    ## @brief Название команды.
    name: str = Field(nullable=False)
    ## @brief Страна, к которой относится команда.
    country: str


## @brief Таблица матчей.
class matches(SQLModel, table=True):
    ## @brief Уникальный идентификатор матча.
    id: int = Field(primary_key=True)
    ## @brief Идентификатор лиги.
    league_id: int = Field(nullable=False)
    ## @brief Сезон проведения матча.
    season: int = Field(nullable=False)
    ## @brief Дата проведения матча.
    match_date: date = Field(nullable=False)
    ## @brief Номер тура.
    round: str = Field(default=None)
    ## @brief Статус матча (завершён, отменён и т.п.).
    status: str = Field(default=None)
    ## @brief Идентификатор домашней команды.
    home_team_id: int = Field(nullable=False)
    ## @brief Идентификатор гостевой команды.
    away_team_id: int = Field(nullable=False)
    ## @brief Голы домашней команды.
    home_goals: int = Field(default=0)
    ## @brief Голы гостевой команды.
    away_goals: int = Field(default=0)


## @brief Связь «команда — лига» (многие-ко-многим).
class team_leagues(SQLModel, table=True):
    ## @brief Идентификатор команды.
    team_id: int = Field(primary_key=True)
    ## @brief Идентификатор лиги.
    league_id: int = Field(nullable=False)


## @brief Пофреймовая статистика команды в рамках матча.
class match_stats(SQLModel, table=True):
    ## @brief Идентификатор матча.
    match_id: int = Field(nullable=False,foreign_key="match_id", primary_key=True)
    ## @brief Идентификатор команды.
    team_id: int = Field(nullable=False,foreign_key="team_id", primary_key=True)
    ## @brief Признак игры дома (True — дома, False — в гостях).
    is_home: bool = Field(nullable=False)
    ## @brief Количество ударов.
    shots: int = Field(default=0)
    ## @brief Количество ударов в створ.
    shots_on_goal: int = Field(default=0)
    ## @brief Количество оффсайдов.
    offsides: int = Field(default=0)
    ## @brief Количество угловых.
    corners: int = Field(default=0)
    ## @brief Количество жёлтых карточек.
    yellow_cards: int = Field(default=0)
    ## @brief Количество красных карточек.
    red_cards: int = Field(default=0)
    ## @brief Процент владения мячом.
    possession: int = Field(default=0)


