from fastapi import FastAPI
from pydantic import BaseModel
from app.routers import stats, teams
from app import crud
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
app = FastAPI()
app.include_router(stats.router)
app.include_router(teams.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
@app.get("/")
def read_index(request: Request):
    crud.teams=crud.get_all_teams()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={teams:crud.teams}
    )
    return FileResponse("app/templates/index.html")