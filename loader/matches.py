import psycopg2
import requests
from psycopg2.extras import execute_values
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    'x-apisports-key': '66fc3cb41a00aa9d22733a9892fec91a'
}
DB = dict(
    host="localhost", port=5432,
    dbname="football", user="postgres", password="1224",
)

def fetch_matches():
    r=requests.get(f"{BASE_URL}/fixtures",
                headers=HEADERS,
                params={"league": 39, "season": "2024"},
                timeout=(10, 180),
                )
    r.raise_for_status()
    return r.json().get("response", [])
def rows_from_response(items):
    rows=[]
    for match in items:
        fixture = match.get("fixture") or {}
        league = match.get("league") or {}
        teams = match.get("teams") or {}
        goals = match.get("goals") or {}
        status = (fixture.get("status") or {}).get("short")
        home_id = (teams.get("home") or {}).get("id")
        away_id = (teams.get("away") or {}).get("id")
        league_id = league.get("id")
        if not (fixture.get("id") and home_id and away_id and league_id):
            continue
        rows.append((
            fixture.get("id"),
            league_id,
            league.get("season"),
            fixture.get("date"),
            league.get("round"),
            status,
            home_id,
            away_id,
            goals.get("home"),
            goals.get("away"),
        ))
    return rows
def upsert(cur, rows):
    execute_values(cur, """
                        INSERT INTO matches (id, league_id, season, match_date, round,
                                             status, home_team_id, away_team_id,
                                             home_goals, away_goals)
                        SELECT v.id,
                               v.league_id,
                               v.season,
                               v.match_date,
                               v.round,
                               v.status,
                               v.home_team_id,
                               v.away_team_id,
                               v.home_goals,
                               v.away_goals
                        FROM (VALUES %s) AS v(
                                              id, league_id, season, match_date, round,
                                              status, home_team_id, away_team_id,
                                              home_goals, away_goals
                            )
                        WHERE EXISTS (SELECT 1 FROM leagues l WHERE l.id = v.league_id)
                          AND EXISTS (SELECT 1 FROM teams t WHERE t.id = v.home_team_id)
                          AND EXISTS (SELECT 1 FROM teams t WHERE t.id = v.away_team_id) ON CONFLICT (id) DO
                        UPDATE SET
                            status = EXCLUDED.status,
                            home_goals = EXCLUDED.home_goals,
                            away_goals = EXCLUDED.away_goals,
                            match_date = EXCLUDED.match_date;
                        """, rows)
def main():
    conn = psycopg2.connect(**DB)
    try:
        with conn, conn.cursor() as cur:
            data = fetch_matches()
            rows = rows_from_response(data)
            if rows:
                upsert(cur, rows)
            print(f"загружено {len(rows)} строк")
    finally:
        conn.close()

if __name__ == "__main__":
    main()