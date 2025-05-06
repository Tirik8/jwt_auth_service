from datetime import datetime
from fastapi import FastAPI

from app import api
from app.core.config import settings
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(api.router, prefix="/api")


@app.get("/")
def read_root():
    return {"status": "ok", "timestamp": datetime.now()}


@app.get("/get_public_rsa_key")
async def get_verify_key():
    return {"rsa_public_key": settings.JWT_PUBLIC_KEY_PATH.read_text()}
