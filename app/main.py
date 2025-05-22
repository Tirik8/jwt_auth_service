from fastapi import FastAPI

from app import api
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(api.router, prefix="/api")

