from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from app import models, config
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from sqlalchemy import create_engine


def get_all_teams():

    return teams
def get_team(team_id: int):
    return teams[team_id]
def get_team_stats(team: schemas.Team,session: Session):
    help_request = select(models.match_stats.team_id,
                          models.match_stats.shots,
                          models.match_stats.shots_on_goal,
                          models.match_stats.offsides,
                          models.match_stats.corners,
                          models.match_stats.yellow_cards,
                          models.match_stats.red_cards,
                          models.match_stats.possession,
                          models.matches.match_date).join(models.matches ,models.match_stats.match_id==models.matches.id) \
        .where(models.match_stats.team_id == team.team_id).order_by(models.matches.match_date)
    if team.where_played==1:
        help_request = help_request.where(models.match_stats.is_home == True)
    if team.where_played==2:
        help_request = help_request.where(models.match_stats.is_home == False)
    help_table = help_request.subquery()
    res=[]
    for stat in team.stats:
        match stat:
            case "shots":
                if team.how_show == 1:
                    request=select(func.avg(help_table.c.shots))
                elif team.how_show == 2:
                    request=select(func.min(help_table.c.shots))
                else:
                    request = select(func.max(help_table.c.shots))
            case "shots_on_goal":
                if team.how_show == 1:
                    request=select(func.avg(help_table.c.shots_on_goal))
                elif team.how_show == 2:
                    request=select(func.min(help_table.c.shots_on_goal))
                else:
                    request = select(func.max(help_table.c.shots_on_goal))
            case "offsides":
                if team.how_show == 1:
                    request=select(func.avg(help_table.c.offsides))
                elif team.how_show == 2:
                    request=select(func.min(help_table.c.offsides))
                else:
                    request = select(func.max(help_table.c.offsides))
            case "corners":
                if team.how_show == 1:
                    request=select(func.avg(help_table.c.corners))
                elif team.how_show == 2:
                    request=select(func.min(help_table.c.corners))
                else:
                    request = select(func.max(help_table.c.corners))
            case "yellow_cards":
                if team.how_show == 1:
                    request=select(func.avg(help_table.c.yellow_cards))
                elif team.how_show == 2:
                    request=select(func.min(help_table.c.yellow_cards))
                else:
                    request = select(func.max(help_table.c.yellow_cards))
            case "red_cards":
                if team.how_show == 1:
                    request=select(func.avg(help_table.c.red_cards))
                elif team.how_show == 2:
                    request=select(func.min(help_table.c.red_cards))
                else:
                    request = select(func.max(help_table.c.red_cards))
            case "possession":
                if team.how_show == 1:
                    request=select(func.avg(help_table.c.possession))
                elif team.how_show == 2:
                    request=select(func.min(help_table.c.possession))
                else:
                    request = select(func.max(help_table.c.possession))
        res.append(round(session.execute(request).scalar(),1))
    return res
