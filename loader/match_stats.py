import time

import psycopg2
import requests
from psycopg2.extras import execute_values

BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    'x-apisports-key': 'a327ccc42c4ef8ad62374237d7e7c585'
}
DB = dict(
    host="localhost", port=5432,
    dbname="football", user="postgres", password="1224",
)

def fetch_stats(fixture_id):
    r=requests.get(f"{BASE_URL}/fixtures/statistics",
                headers=HEADERS,
                params={"fixture": fixture_id},
                timeout=(20, 180),
                )
    r.raise_for_status()
    return r.json().get("response", [])
def rows_from_response(items, match_id, cur):
    rows = []
    for item in items:
        team = item.get("team") or {}
        stats = item.get("statistics") or []
        team_id = team.get("id")
        if not team_id:
            continue

        stat_map = {s.get("type"): s.get("value") for s in stats}

        def to_int(v):
            if v is None:
                return 0
            if isinstance(v, str):
                v = v.replace("%", "").strip()
                if v == "":
                    return 0
                try:
                    return int(v)
                except ValueError:
                    return 0
            return int(v)

        cur.execute(
            "SELECT home_team_id, away_team_id FROM matches WHERE id = %s",
            (match_id,),
        )
        row = cur.fetchone()
        if not row:
            continue
        home_id, away_id = row
        if team_id == home_id:
            is_home = True
        elif team_id == away_id:
            is_home = False
        else:
            continue

        rows.append((
            match_id,
            team_id,
            is_home,
            to_int(stat_map.get("Total Shots")),
            to_int(stat_map.get("Shots on Goal")),
            to_int(stat_map.get("Offsides")),
            to_int(stat_map.get("Corner Kicks")),
            to_int(stat_map.get("Yellow Cards")),
            to_int(stat_map.get("Red Cards")),
            to_int(stat_map.get("Ball Possession")),
        ))
    return rows
def upsert(cur, rows):
    execute_values(cur, """
                        INSERT INTO match_stats (match_id, team_id, is_home,
                                                 shots, shots_on_goal, offsides,
                                                 corners, yellow_cards, red_cards,
                                                 possession)
                        SELECT v.match_id,
                               v.team_id,
                               v.is_home,
                               v.shots,
                               v.shots_on_goal,
                               v.offsides,
                               v.corners,
                               v.yellow_cards,
                               v.red_cards,
                               v.possession
                        FROM (VALUES %s) AS v(
                                              match_id, team_id, is_home,
                                              shots, shots_on_goal, offsides,
                                              corners, yellow_cards, red_cards,
                                              possession
                            )
                        WHERE EXISTS (SELECT 1 FROM matches m WHERE m.id = v.match_id)
                          AND EXISTS (SELECT 1 FROM teams t WHERE t.id = v.team_id) ON CONFLICT (match_id, team_id) DO
                        UPDATE SET
                            is_home = EXCLUDED.is_home,
                            shots = EXCLUDED.shots,
                            shots_on_goal = EXCLUDED.shots_on_goal,
                            offsides = EXCLUDED.offsides,
                            corners = EXCLUDED.corners,
                            yellow_cards = EXCLUDED.yellow_cards,
                            red_cards = EXCLUDED.red_cards,
                            possession = EXCLUDED.possession;
                        """, rows)
def main():
    conn = psycopg2.connect(**DB)
    total = 0
    list={ 1208402}
    try:
        with conn, conn.cursor() as cur:
            for i in list:
                try:
                    data = fetch_stats(i)
                except requests.HTTPError as e:
                    print(f"fixture {i}: HTTP error {e}")
                    continue

                rows = rows_from_response(data, i, cur)
                if rows:
                    upsert(cur, rows)
                    total += len(rows)
                    print(f"fixture {i}: +{len(rows)}")
                else:
                    print(f"fixture {i}: пусто (response={len(data)})")
                time.sleep(1)
        print(f"загружено {total} строк")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
