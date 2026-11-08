from app import crud
from app import schemas, config
from fastapi import APIRouter, Request
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
@router.get("/")
def get_all_teams(request: Request,sesssion: Session = Depends(config.get_session)):
        crud.teams = crud.get_all_teams(sesssion)
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"teams": crud.teams}
        )
@router.get("/teams/{team_id}")
def get_team(team_id: int):
    crud.get_team(team_id)