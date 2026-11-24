from pydantic import BaseModel
from typing import List
class Team(BaseModel):
    team_id: int
    matches_count: int
    where_played: int
    how_show: int
    stats: List[str]
class TeamTrend(BaseModel):
    team_id: int
    matches_count: int
    where_played: int
    stats: str