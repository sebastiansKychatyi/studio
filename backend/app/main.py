"""Duo Studio team API: login, kanban boards and alarms.

Nuxt proxies /api/team/** to this app (see server/api/team/[...path].ts).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import settings
from .db import engine
from .models import Base
from .routers import alarms, auth, kanban

PREFIX = "/api/team"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create missing tables (no migrations yet)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Duo Studio team API",
    lifespan=lifespan,
    docs_url=f"{PREFIX}/docs" if settings.docs else None,
    redoc_url=None,
    openapi_url=f"{PREFIX}/openapi.json" if settings.docs else None,
)

for r in (auth.router, kanban.router, alarms.router):
    app.include_router(r, prefix=PREFIX)


@app.get(f"{PREFIX}/health", tags=["meta"])
async def health():
    return {"ok": True}
