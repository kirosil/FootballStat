import requests
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {'x-apisports-key': os.getenv('API_PASS')}

r = requests.get(
    f"{BASE_URL}/fixtures/statistics",
    headers=HEADERS,
    params={"fixture": 1208021},
    timeout=(10, 180),
)
print("HTTP:", r.status_code)
print("URL:", r.url)
print("BODY:", r.text[:1000])