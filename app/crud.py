from sqlalchemy import select, func, and_, desc, ColumnElement
from sqlalchemy.orm import Session
from app import models, config, schemas
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from sqlalchemy import create_engine
from typing import Any


def get_all_teams(session: Session):
    teams_name={}
    request=(select(models.teams.id,models.teams.name).join(models.team_leagues, models.teams.id== models.team_leagues.team_id)
             .group_by(models.teams.id,models.teams.name)
             .order_by(models.teams.id,models.teams.name))
    rows=session.execute(request).all()
    return {team_id: name for team_id, name in rows}
def get_team(session: Session, team_id: int):
    request=select(models.teams.name).where(models.teams.id==team_id)
    team_by_id=session.execute(request).scalars().all()
    return team_by_id
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
        .where(models.match_stats.team_id == team.team_id).order_by(desc(models.matches.match_date)).limit(team.matches_count)
    if team.where_played==1:
        help_request = help_request.where(models.match_stats.is_home == True)
    if team.where_played==2:
        help_request = help_request.where(models.match_stats.is_home == False)
    help_table = help_request.subquery()
    res=[]
    for stat in team.stats:
        match stat:
            case "shots":
                request = agg(help_table.c.shots, team.how_show)
            case "shots_on_goal":
                request = agg(help_table.c.shots_on_goal, team.how_show)
            case "offsides":
                request = agg(help_table.c.offsides, team.how_show)
            case "corners":
                request = agg(help_table.c.corners, team.how_show)
            case "yellow_cards":
                request = agg(help_table.c.yellow_cards, team.how_show)
            case "red_cards":
                request = agg(help_table.c.red_cards, team.how_show)
            case "possession":
                request = agg(help_table.c.possession, team.how_show)

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
            compare_res.append(None)
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
                          models.matches.match_date,
                          models.matches.home_team_id,
        models.matches.away_team_id).join(models.matches,
                                                          models.match_stats.match_id == models.matches.id) \
        .where(models.match_stats.team_id == team.team_id).order_by(desc(models.matches.match_date)).limit(team.matches_count)
    opp_is_home=False;
    opp_is_away=False;
    if team.where_played==1:
        help_request = help_request.where(models.match_stats.is_home == True)
        opp_is_away=True
    if team.where_played==2:
        help_request = help_request.where(models.match_stats.is_home == False)
        opp_is_home=True
    help_table = help_request.subquery()
    res =[]
    team_ids =[]
    stat=team.stats

    for i in range(0,team.matches_count):
        if opp_is_home:
            request2 = select(help_table.c.home_team_id).offset(i)
        elif opp_is_away:
            request2=select(help_table.c.away_team_id).offset(i)
        else:
            home_id = session.execute(select(help_table.c.home_team_id).offset(i)).scalar()
            if home_id==team.team_id:
                request2 = select(help_table.c.away_team_id).offset(i)
            else:
                request2 = select(help_table.c.home_team_id).offset(i)
        match stat:
            case "shots":
                request = agg_compare(help_table.c.shots,i)
            case "shots_on_goal":
                request = agg_compare(help_table.c.shots_on_goal,i)
            case "offsides":
                request = agg_compare(help_table.c.offsides,i)
            case "corners":
                request = agg_compare(help_table.c.corners,i)
            case "yellow_cards":
                request = agg_compare(help_table.c.yellow_cards,i)
            case "red_cards":
                request = agg_compare(help_table.c.red_cards,i)
            case "possession":
                request = agg_compare(help_table.c.possession,i)

        res.append(round(session.execute(request).scalar(),1))
        team_ids.append(session.execute(request2).scalar())
    team_names=[]
    for item in team_ids:
        team_names.append(get_team(session,item))
    return res, [row[0] for row in team_names]
def agg(col: ColumnElement[Any], how_show: int):
    if how_show == 1:
        request = select(func.avg(col))
    elif how_show == 2:
        request = select(func.min(col))
    else:
        request = select(func.max(col))
    return request
def agg_compare(col: ColumnElement[Any], i:int):
    request = select(col).limit(1).offset(i)
    return request