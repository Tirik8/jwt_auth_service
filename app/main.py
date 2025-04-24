from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth, users
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Auth Service"}