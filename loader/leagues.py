
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
def fetch_leagues():
    r = requests.get(
        f"{BASE_URL}/leagues",
        headers=HEADERS,
        params={"season": "2024"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("response", [])
def rows_from_response(items):
    rows = []
    for item in items:
        lg = item["league"]
        country = (item.get("country") or {}).get("name")
        logo = f"https://media.api-sports.io/football/leagues/{lg['id']}.png"
        for s in item.get("seasons", []):
            rows.append((
                lg["id"],
                s["year"],
                lg["name"],
                country,
                logo,
            ))
    return rows
def upsert(cur, rows):
    execute_values(cur, """
        INSERT INTO leagues (id, season, name, country, logo_url)
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET
            name     = EXCLUDED.name,
            country  = EXCLUDED.country,
            logo_url = EXCLUDED.logo_url;
    """, rows)

def main():
    conn = psycopg2.connect(**DB)
    try:
        with conn, conn.cursor() as cur:
            data = fetch_leagues()
            rows = rows_from_response(data)
            if rows:
                upsert(cur, rows)
            print(f"загружено {len(rows)} строк")
    finally:
        conn.close()

if __name__ == "__main__":
    main()