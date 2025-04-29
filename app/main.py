from datetime import datetime
from fastapi import FastAPI

from app import api
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(api.router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "ok", "timestamp": datetime.now()}
