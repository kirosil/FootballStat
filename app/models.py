from sqlmodel import SQLModel, create_engine, Field, Session
class teams (SQLModel, table=True):
    id :int =Field(primary_key=True)
    name:str =Field(nullable=False)
    country: str
class matches (SQLModel, table=True):
    id :int =Field(primary_key=True)
    league_id: int =Field(nullable=False)
    season: int =Field(nullable=False)
    match_date:str =Field(nullable=False)
    round:str =Field(default=None)
    status:str =Field(default=None)
    home_team_id: int =Field(nullable=False)
    away_team_id: int    =Field(nullable=False)
    home_goals: int =Field(default=0)
    away_goals: int=Field(default=0)



class match_stats (SQLModel, table=True):
    match_id        :int =Field(primary_key=True)
    team_id: int =Field(nullable=False)
    is_home: bool=Field(nullable=False)
    shots: int =Field(default=0)
    shots_on_goal: int=Field(default=0)
    offsides: int=Field(default=0)
    corners: int=Field(default=0)
    yellow_cards: int=Field(default=0)
    red_cards: int=Field(default=0)
    possession: int=Field(default=0)

