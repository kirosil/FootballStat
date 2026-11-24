"""
@file stats.py
@brief HTTP-эндпоинты для аналитики статистики.

Предоставляет три POST-эндпоинта: статистика команды, сравнение
двух команд и тренд метрики. Все эндпоинты возвращают JSON.
"""

from app import schemas, config, crud
from fastapi import APIRouter, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, status
router = APIRouter()



@router.post("/stats/team")
def get_team_stats(request: Request, team: schemas.Team,
                   session: Session = Depends(config.get_session)):
    """
    @brief Возвращает агрегированную статистику одной команды.

    @param request Объект запроса FastAPI.
    @param team Параметры запроса (см. schemas.Team).
    @param session Сессия БД (dependency).
    @return list[float] Список агрегированных значений метрик.
    """
    if (team.matches_count==0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо выбрать хотя бы 1 матч")
    if (team.matches_count>38):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо выбрать не более 38 матчей")
    stats = crud.get_team_stats(team, session)
    return stats


@router.post("/stats/compare")
def compare_teams_stats(team: schemas.Team, team2: schemas.Team,
                        session: Session = Depends(config.get_session)):
    """
    @brief Сравнивает статистику двух команд.

    @param team Параметры первой команды.
    @param team2 Параметры второй команды.
    @param session Сессия БД (dependency).
    @return tuple[list, list, list] Победители по метрикам и значения
            статистики каждой команды.
    """
    if (team.matches_count==0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо выбрать хотя бы 1 матч")
    if (team2.matches_count==0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо выбрать хотя бы 1 матч")
    if (team.matches_count>38):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо выбрать не более 38 матчей")
    if (team2.matches_count>38):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо выбрать не более 38 матчей")
    return (crud.compare_teams_stats(team, team2, session),
            crud.get_team_stats(team, session),
            crud.get_team_stats(team2, session))


@router.post("/stats/trend")
def get_team_trend(team: schemas.TeamTrend,
                   session: Session = Depends(config.get_session)):
    """
    @brief Возвращает тренд выбранной метрики команды по матчам.

    @param team Параметры запроса (см. schemas.TeamTrend).
    @param session Сессия БД (dependency).
    @return tuple[list[float], list[str]] Значения метрики и имена соперников.
    """
    if (team.matches_count==0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо выбрать хотя бы 1 матч")
    if (team.matches_count>38):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо выбрать не более 38 матчей")
    return crud.get_team_trend(team, session)
