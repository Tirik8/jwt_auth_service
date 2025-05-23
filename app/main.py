from fastapi import FastAPI
from contextlib import asynccontextmanager

from app import api
from app.api.root import router as root_router

from app.db.database import engine
from app.db import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(api.router, prefix="/api")
app.include_router(root_router, prefix="")
