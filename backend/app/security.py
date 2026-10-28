import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import get_db
from .models import Session, User

# Used to keep login timing equal for unknown usernames
_DUMMY_HASH = bcrypt.hashpw(b"dummy", bcrypt.gensalt()).decode()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()


def verify_password(password: str, password_hash: str | None) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), (password_hash or _DUMMY_HASH).encode()) and password_hash is not None
    except ValueError:
        return False


def _sha(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def create_session(db: AsyncSession, response: Response, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    ttl = timedelta(days=settings.session_days)
    await db.execute(delete(Session).where(Session.expires_at < _now()))
    db.add(Session(token_hash=_sha(token), user_id=user_id, expires_at=_now() + ttl))
    await db.commit()
    response.set_cookie(
        settings.cookie_name,
        token,
        max_age=int(ttl.total_seconds()),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


async def destroy_session(db: AsyncSession, request: Request, response: Response) -> None:
    token = request.cookies.get(settings.cookie_name)
    if token:
        await db.execute(delete(Session).where(Session.token_hash == _sha(token)))
        await db.commit()
    response.delete_cookie(settings.cookie_name, path="/")


async def optional_user(request: Request, db: AsyncSession = Depends(get_db)) -> User | None:
    token = request.cookies.get(settings.cookie_name)
    if not token:
        return None
    return await db.scalar(
        select(User).join(Session, Session.user_id == User.id).where(Session.token_hash == _sha(token), Session.expires_at > _now())
    )


async def current_user(user: User | None = Depends(optional_user)) -> User:
    if user is None:
        raise HTTPException(401, "Not authenticated")
    return user
