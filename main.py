import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        app=settings.APP, 
        host=settings.HOST, 
        port=settings.PORT, 
        log_level=settings.LOG_LEVEL,
    )