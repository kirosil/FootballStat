from fastapi import FastAPI
from pydantic import BaseModel
from app.routers import stats
app = FastAPI()
app.include_router(stats.router)
