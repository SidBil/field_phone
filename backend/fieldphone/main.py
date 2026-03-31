from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from fieldphone.api.router import api_router
from fieldphone.config import settings
from fieldphone.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.audio_dir.mkdir(parents=True, exist_ok=True)
    settings.sessions_dir.mkdir(parents=True, exist_ok=True)

    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Phoneme classification and database management for field linguists",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

if settings.audio_dir.exists():
    app.mount(
        "/audio",
        StaticFiles(directory=str(settings.audio_dir)),
        name="audio",
    )
