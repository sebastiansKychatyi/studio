"""Duo Studio team API: login, kanban boards, alarms, expenses and income.

Nuxt proxies /api/team/** to this app (see server/api/team/[...path].ts).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import inspect, text

from .config import settings
from .db import engine
from .models import Base
from .routers import alarms, auth, events, kanban, money, settings as settings_router

PREFIX = "/api/team"

# Columns added after the first release: (table, column, SQL type)
ADDED_COLUMNS = [
    ("cards", "due_date", "DATE"),
    ("cards", "is_private", "BOOLEAN NOT NULL DEFAULT FALSE"),
    ("boards", "is_private", "BOOLEAN NOT NULL DEFAULT FALSE"),
    ("expenses", "recurring_id", "INTEGER REFERENCES recurring(id) ON DELETE SET NULL"),
    ("incomes", "recurring_id", "INTEGER REFERENCES recurring(id) ON DELETE SET NULL"),
    ("events", "remind", "INTEGER"),
]


def _upgrade(conn) -> None:
    """Create missing tables and add new columns to existing ones (no migrations yet)."""
    had_members = inspect(conn).has_table("board_members")
    Base.metadata.create_all(conn)
    insp = inspect(conn)
    for table, column, sql_type in ADDED_COLUMNS:
        if column not in {c["name"] for c in insp.get_columns(table)}:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))
    if not had_members:
        _share_team_boards(conn)


def _share_team_boards(conn) -> None:
    """One-time switch to per-person access: a former team board stays shared
    only with people who already worked on it (created or were assigned a card)."""
    rows = conn.execute(
        text(
            "SELECT b.id, b.created_by, c.created_by, c.assignee_id FROM boards b "
            "JOIN board_columns bc ON bc.board_id = b.id JOIN cards c ON c.column_id = bc.id "
            "WHERE b.is_private = :no"
        ),
        {"no": False},
    )
    pairs = set()
    for board_id, owner, author, assignee in rows:
        for uid in (author, assignee):
            if uid is not None and uid != owner:
                pairs.add((board_id, uid))
    for board_id, uid in sorted(pairs):
        conn.execute(text("INSERT INTO board_members (board_id, user_id) VALUES (:b, :u)"), {"b": board_id, "u": uid})


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

for r in (auth.router, kanban.router, alarms.router, money.router, events.router, settings_router.router):
    app.include_router(r, prefix=PREFIX)


@app.get(f"{PREFIX}/health", tags=["meta"])
async def health():
    return {"ok": True}
