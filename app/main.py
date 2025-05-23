from fastapi import FastAPI

from app import api
from app.api.root import router as root_router

from app.db.database import engine
from app.db import models

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

app.include_router(api.router, prefix="/api")
app.include_router(root_router, prefix="")
