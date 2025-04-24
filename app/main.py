from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, users
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
#
#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=settings.BACKEND_CORS_ORIGINS,
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Auth Service"}