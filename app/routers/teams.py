"""
@file teams.py
@brief HTTP-эндпоинты для рендеринга HTML-страниц.

Отдаёт главную страницу, страницу сравнения и страницу графика,
передавая в шаблоны список команд.
"""

from app import crud
from app import schemas, config
from fastapi import APIRouter, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def get_all_teams(request: Request, session: Session = Depends(config.get_session)):
    """
    @brief Главная страница со статистикой одной команды.

    @param request Объект запроса FastAPI.
    @param session Сессия БД (dependency).
    @return TemplateResponse HTML-страница index.html со списком команд.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"teams": crud.get_all_teams(session)}
    )


@router.get("/compare")
def read_compare(request: Request, session: Session = Depends(config.get_session)):
    """
    @brief Страница сравнения двух команд.

    @param request Объект запроса FastAPI.
    @param session Сессия БД (dependency).
    @return TemplateResponse HTML-страница compare.html.
    """
    return templates.TemplateResponse(
        request=request,
        name="compare.html",
        context={"teams": crud.get_all_teams(session)}
    )


@router.get("/graph")
def show_graph(request: Request, session: Session = Depends(config.get_session)):
    """
    @brief Страница графика тренда команды.

    @param request Объект запроса FastAPI.
    @param session Сессия БД (dependency).
    @return TemplateResponse HTML-страница graph.html.
    """

    return templates.TemplateResponse(
        request=request,
        name="graph.html",
        context={"teams": crud.get_all_teams(session)}
    )