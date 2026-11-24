from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import Session
from app import models, config, schemas
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from sqlalchemy import create_engine

teams={}

def get_all_teams(session: Session):
    teams_name={}
    request=(select(models.team_leagues.team_id).group_by(models.team_leagues.team_id)
             .order_by(models.team_leagues.team_id))
    all_team_id=session.execute(request).scalars().all()
    for i in all_team_id:
        request2=(select(models.teams.name).where(models.teams.id==i))
        team=session.execute(request2).scalars().all()
        teams_name[i]=team
    return teams_name   
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
        res.append(round(session.execute(request).scalar(),1))
        team_ids.append(session.execute(request2).scalar())
    team_names=[]
    for item in team_ids:
        team_names.append(get_team(session,item))
    return res, [row[0] for row in team_names]
