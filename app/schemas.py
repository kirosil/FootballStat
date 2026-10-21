from pydantic import BaseModel
class Team(BaseModel):
    name: str
    team_id: int
    matches_count: int
    where_played: int
    how_show: int
    stats: list[str]