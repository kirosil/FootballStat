from fastapi import FastAPI
from app.routers import stats, teams
from fastapi.staticfiles import StaticFiles
app = FastAPI()
app.include_router(stats.router)
app.include_router(teams.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


