from app import crud, models, schemas
router = APIRouter()
@router.get("/teams")
def get_all_teams():
    crud.get_all_teams()
@router.get("/teams/{team_id}")
def get_team(team_id: int):
    crud.get_team(team_id)