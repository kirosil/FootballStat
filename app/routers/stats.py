from app import crud
from app import schemas, config
from fastapi import APIRouter
from fastapi.params import Depends
router = APIRouter()
@router.get("/stats/team")
def get_team_stats(team: schemas.Team, session: Session = Depends(config.get_session)):
    return crud.get_team_stats(team, session);
@router.get("/stats/compare")
def compare_teams_stats(team: schemas.Team, team2: schemas.Team, session: Session = Depends(config.get_session)):
    return crud.compare_teams_stats(team, team2, session);

