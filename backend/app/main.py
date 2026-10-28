"""Duo Studio team API: login, kanban boards, alarms, expenses and income.

Nuxt proxies /api/team/** to this app (see server/api/team/[...path].ts).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import inspect, text

from .config import settings
from .db import engine
from .models import Base
from .routers import alarms, auth, kanban, money

PREFIX = "/api/team"

# Columns added after the first release: (table, column, SQL type)
ADDED_COLUMNS = [("cards", "due_date", "DATE")]


def _upgrade(conn) -> None:
    """Create missing tables and add new nullable columns to existing ones (no migrations yet)."""
    Base.metadata.create_all(conn)
    insp = inspect(conn)
    for table, column, sql_type in ADDED_COLUMNS:
        if column not in {c["name"] for c in insp.get_columns(table)}:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(_upgrade)
    yield
    await engine.dispose()


app = FastAPI(
    title="Duo Studio team API",
    lifespan=lifespan,
    docs_url=f"{PREFIX}/docs" if settings.docs else None,
    redoc_url=None,
    openapi_url=f"{PREFIX}/openapi.json" if settings.docs else None,
)

for r in (auth.router, kanban.router, alarms.router, money.router):
    app.include_router(r, prefix=PREFIX)


@app.get(f"{PREFIX}/health", tags=["meta"])
async def health():
    return {"ok": True}
