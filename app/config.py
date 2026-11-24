from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DATABASE_URL")
if not api_key:
    raise RuntimeError("DATABASE_URL не задан")

engine=create_engine(api_key)

def get_session():
    with Session(engine) as session:
        yield session