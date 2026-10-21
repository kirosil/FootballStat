from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from sqlalchemy import create_engine
engine=create_engine('postgresql://postgres:1224@localhost:5432/football')

def get_session():
    with Session(engine) as session:
        yield session