from pydantic import BaseModel
from typing import List
class Team(BaseModel):
    name: str
    team_id: int
    matches_count: int
    where_played: int
    how_show: int
    stats: List[str]
class TeamTrend(BaseModel):
    name: str
    team_id: int
    matches_count: int
    where_played: int
    stats: List[str]