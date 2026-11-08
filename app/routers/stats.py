from app import crud
from app import schemas, config
from fastapi import APIRouter, Request
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
@router.post("/stats/team")
def get_team_stats(request: Request, team: schemas.Team, session: Session = Depends(config.get_session)):
    stats = crud.get_team_stats(team, session)
    return  templates.TemplateResponse(
        request=request,
        name="match_stat.html",
        context={"stats": stats},
    )
@router.get("/stats/compare")
def compare_teams_stats(team: schemas.Team, team2: schemas.Team, session: Session = Depends(config.get_session)):
    return crud.compare_teams_stats(team, team2, session)
@router.get("/stats/trend")
def get_team_trend(team: schemas.TeamTrend, session: Session = Depends(config.get_session)):
    return crud.get_team_trend(team, session)
