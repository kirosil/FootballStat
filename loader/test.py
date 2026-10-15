import requests
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {'x-apisports-key': '66fc3cb41a00aa9d22733a9892fec91a'}

r = requests.get(
    f"{BASE_URL}/fixtures/statistics",
    headers=HEADERS,
    params={"fixture": 1208021},
    timeout=(10, 180),
)
print("HTTP:", r.status_code)
print("URL:", r.url)
print("BODY:", r.text[:1000])