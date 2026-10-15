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
def fetch_teams():
    r=requests.get(f"{BASE_URL}/teams",
                headers=HEADERS,
                params={"league": 39, "season": 2024},
                timeout=30,
                )
    r.raise_for_status()
    return r.json().get("response", [])
def rows_from_response(items):
    rows=[]
    for team in items:
        team=team.get("team") or {}
        rows.append((
            team.get("id"),
            39,
        ))
    return rows
def upsert(cur, rows):
    execute_values(cur, """
    INSERT INTO team_leagues (team_id, league_id)
    VALUES %s
        ON CONFLICT (team_id,league_id) DO NOTHING;""",rows)
def main():
    conn = psycopg2.connect(**DB)
    try:
        with conn, conn.cursor() as cur:
            data = fetch_teams()
            rows = rows_from_response(data)
            if rows:
                upsert(cur, rows)
            print(f"загружено {len(rows)} строк")
    finally:
        conn.close()

if __name__ == "__main__":
    main()