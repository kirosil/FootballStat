"""
@file crud.py
@brief Бизнес-логика запросов к базе данных.

Содержит функции получения списка команд, агрегированной статистики,
сравнения двух команд и построения тренда по матчам. Все функции
принимают активную сессию SQLAlchemy и не управляют её жизненным циклом.
"""

from sqlalchemy import select, func, and_, desc, ColumnElement
from sqlalchemy.orm import Session
from app import models, schemas
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from typing import Any


def get_all_teams(session: Session):
    """
    @brief Возвращает словарь всех команд, участвующих хотя бы в одной лиге.

    @param session Активная сессия SQLAlchemy.
    @return dict[int, str] Словарь вида {id_команды: название}.
    """
    teams_name = {}
    request = (select(models.teams.id, models.teams.name)
               .join(models.team_leagues, models.teams.id == models.team_leagues.team_id)
               .group_by(models.teams.id, models.teams.name)
               .order_by(models.teams.id, models.teams.name))
    rows = session.execute(request).all()
    return {team_id: name for team_id, name in rows}


def get_team(session: Session, team_id: int):
    """
    @brief Возвращает название команды по её идентификатору.

    @param session Активная сессия SQLAlchemy.
    @param team_id Идентификатор команды.
    @return list[str] Список из одного элемента с названием команды
            (пустой список, если команда не найдена).
    """
    request = select(models.teams.name).where(models.teams.id == team_id)
    team_by_id = session.execute(request).scalars().all()
    return team_by_id


def get_team_stats(team: schemas.Team, session: Session):
    """
    @brief Вычисляет агрегированную статистику команды по выбранным метрикам.

    Учитываются последние `team.matches_count` матчей; при необходимости
    фильтруются только домашние или только гостевые игры.

    @param team Параметры запроса (см. schemas.Team).
    @param session Активная сессия SQLAlchemy.
    @return list[float] Список агрегированных значений в порядке метрик из `team.stats`.
    @throws UnboundLocalError Если в `team.stats` передана неизвестная метрика.
    """
    help_request = select(
        models.match_stats.team_id,
        models.match_stats.shots,
        models.match_stats.shots_on_goal,
        models.match_stats.offsides,
        models.match_stats.corners,
        models.match_stats.yellow_cards,
        models.match_stats.red_cards,
        models.match_stats.possession,
        models.matches.match_date
    ).join(
        models.matches, models.match_stats.match_id == models.matches.id
    ).where(
        models.match_stats.team_id == team.team_id
    ).order_by(
        desc(models.matches.match_date)
    ).limit(team.matches_count)

    if team.where_played == 1:
        help_request = help_request.where(models.match_stats.is_home == True)
    if team.where_played == 2:
        help_request = help_request.where(models.match_stats.is_home == False)
    help_table = help_request.subquery()
    res = []
    for stat in team.stats:
        match stat:
            case "shots":
                request = agg(help_table.c.shots, team.how_show)
            case "shots_on_goal":
                request = agg(help_table.c.shots_on_goal, team.how_show)
            case "offsides":
                request = agg(help_table.c.offsides, team.how_show)
            case "corners":
                request = agg(help_table.c.corners, team.how_show)
            case "yellow_cards":
                request = agg(help_table.c.yellow_cards, team.how_show)
            case "red_cards":
                request = agg(help_table.c.red_cards, team.how_show)
            case "possession":
                request = agg(help_table.c.possession, team.how_show)
        res.append(round(session.execute(request).scalar(), 1))
    return res


def compare_teams_stats(team: schemas.Team, team2: schemas.Team, session: Session):
    """
    @brief Сравнивает агрегированные метрики двух команд.

    Для каждой метрики определяется, какая команда имеет большее значение.
    При равенстве возвращается `None`.

    @param team Параметры первой команды.
    @param team2 Параметры второй команды.
    @param session Активная сессия SQLAlchemy.
    @return list[Optional[int]] Список победителей (0, 1) в зависимоти о том какая из переданных команд победила
            по каждой метрике (или 3 при равенстве).
    """
    compare_res = []
    team1_res = get_team_stats(team, session)
    team2_res = get_team_stats(team2, session)
    for i in range(0, len(team.stats)):
        if team1_res[i] > team2_res[i]:
            compare_res.append(0)
        if team2_res[i] > team1_res[i]:
            compare_res.append(1)
        if team1_res[i] == team2_res[i]:
            compare_res.append(3)
    return compare_res


def get_team_trend(team: schemas.TeamTrend, session: Session):
    """
    @brief Строит тренд выбранной метрики команды по последним матчам.

    @param team Параметры запроса тренда (см. schemas.TeamTrend).
    @param session Активная сессия SQLAlchemy.
    @return tuple[list[float], list[str]] Кортеж из двух списков:
            значения метрики и названия команд-соперников.
    @throws UnboundLocalError Если передана неизвестная метрика.
    """
    help_request = select(
        models.match_stats.team_id,
        models.match_stats.shots,
        models.match_stats.shots_on_goal,
        models.match_stats.offsides,
        models.match_stats.corners,
        models.match_stats.yellow_cards,
        models.match_stats.red_cards,
        models.match_stats.possession,
        models.matches.match_date,
        models.matches.home_team_id,
        models.matches.away_team_id
    ).join(
        models.matches, models.match_stats.match_id == models.matches.id
    ).where(
        models.match_stats.team_id == team.team_id
    ).order_by(
        desc(models.matches.match_date)
    ).limit(team.matches_count)

    opp_is_home = False
    opp_is_away = False
    if team.where_played == 1:
        help_request = help_request.where(models.match_stats.is_home == True)
        opp_is_away = True
    if team.where_played == 2:
        help_request = help_request.where(models.match_stats.is_home == False)
        opp_is_home = True
    help_table = help_request.subquery()
    res = []
    team_ids = []
    stat = team.stats

    for i in range(0, team.matches_count):
        if opp_is_home:
            request2 = select(help_table.c.home_team_id).offset(i)
        elif opp_is_away:
            request2 = select(help_table.c.away_team_id).offset(i)
        else:
            home_id = session.execute(select(help_table.c.home_team_id).offset(i)).scalar()
            if home_id == team.team_id:
                request2 = select(help_table.c.away_team_id).offset(i)
            else:
                request2 = select(help_table.c.home_team_id).offset(i)
        match stat:
            case "shots":
                request = agg_compare(help_table.c.shots, i)
            case "shots_on_goal":
                request = agg_compare(help_table.c.shots_on_goal, i)
            case "offsides":
                request = agg_compare(help_table.c.offsides, i)
            case "corners":
                request = agg_compare(help_table.c.corners, i)
            case "yellow_cards":
                request = agg_compare(help_table.c.yellow_cards, i)
            case "red_cards":
                request = agg_compare(help_table.c.red_cards, i)
            case "possession":
                request = agg_compare(help_table.c.possession, i)

        res.append(round(session.execute(request).scalar(), 1))
        team_ids.append(session.execute(request2).scalar())

    team_names = []
    for item in team_ids:
        team_names.append(get_team(session, item))
    return res, [row[0] for row in team_names]


def agg(col: ColumnElement[Any], how_show: int):
    """
    @brief Формирует SQL-запрос агрегации по колонке.

    @param col Колонка, к которой применяется агрегация.
    @param how_show Тип агрегации: 1 — avg, 2 — min, иначе — max.
    @return Select Скалярный SELECT-запрос.
    """
    if how_show == 1:
        request = select(func.avg(col))
    elif how_show == 2:
        request = select(func.min(col))
    else:
        request = select(func.max(col))
    return request


def agg_compare(col: ColumnElement[Any], i: int):
    """
    @brief Формирует SELECT-запрос значения колонки для i-й строки.

    @param col Колонка выборки.
    @param i Смещение строки (0 — самая свежая).
    @return Select Скалярный SELECT-запрос с LIMIT 1 OFFSET i.
    """
    request = select(col).limit(1).offset(i)
    return request