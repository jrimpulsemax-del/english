from fastapi import FastAPI

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.routers import ai, auth, users

app = FastAPI(title=settings.app_name)


@app.on_event('startup')
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get('/health')
def health_check():
    return {'status': 'ok'}


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(ai.router, prefix=settings.api_v1_prefix)
