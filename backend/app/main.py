from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import build_router
from app.config import settings


app = FastAPI(title=settings.app_name)
app.include_router(build_router())


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "description": "Citation review and reference refactor service",
        "docs": "/docs",
    }
