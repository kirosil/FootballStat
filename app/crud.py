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
        .where(models.match_stats.team_id == team.team_id).order_by(models.matches.match_date).limit(team.matches_count)
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
def compare_teams_stats(team: schemas.Team, team2: schemas.Team, session: Session):
    compare_res=[]
    team1_res=get_team_stats(team,session)
    team2_res=get_team_stats(team2,session)
    for i in range(0,len(team.stats)):
        if team1_res[i]>team2_res[i]:
            compare_res.append(team.team_id)
        if team2_res[i]>team1_res[i]:
            compare_res.append(team2.team_id)
        if team1_res[i]==team2_res[i]:
            compare_res.append(team.team_id+team2.team_id+1)
    return compare_res
def get_team_trend(team: schemas.TeamTrend, session: Session):
    help_request = select(models.match_stats.team_id,
                          models.match_stats.shots,
                          models.match_stats.shots_on_goal,
                          models.match_stats.offsides,
                          models.match_stats.corners,
                          models.match_stats.yellow_cards,
                          models.match_stats.red_cards,
                          models.match_stats.possession,
                          models.matches.match_date).join(models.matches,
                                                          models.match_stats.match_id == models.matches.id) \
        .where(models.match_stats.team_id == team.team_id).order_by(models.matches.match_date).limit(team.matches_count)
    if team.where_played==1:
        help_request = help_request.where(models.match_stats.is_home == True)
    if team.where_played==2:
        help_request = help_request.where(models.match_stats.is_home == False)
    help_table = help_request.subquery()
    res = [[]for j in range(team.matches_count)]
    for i in range(0,team.matches_count):
        for stat in team.stats:
            match stat:
                case "shots":
                    request=select(help_table.c.shots).limit(1).offset(i)
                case "shots_on_goal":
                    request = select(help_table.c.shots_on_goal).limit(1).offset(i)
                case "offsides":
                    request = select(help_table.c.offsides).limit(1).offset(i)
                case "corners":
                    request = select(help_table.c.corners).limit(1).offset(i)
                case "yellow_cards":
                    request = select(help_table.c.yellow_cards).limit(1).offset(i)
                case "red_cards":
                    request = select(help_table.c.red_cards).limit(1).offset(i)
                case "possession":
                    request = select(help_table.c.possession).limit(1).offset(i)
            res[i].append(round(session.execute(request).scalar(),1))
    return res
