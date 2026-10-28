import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import User
from ..schemas import LoginIn, MeOut, UserOut
from ..security import create_session, current_user, destroy_session, optional_user, verify_password

router = APIRouter(tags=["auth"])

# 10 failed logins per 15 min per IP (in memory)
_FAILS: dict[str, list[float]] = defaultdict(list)
_WINDOW = 15 * 60


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    return forwarded.split(",")[0].strip() or (request.client.host if request.client else "unknown")


@router.post("/auth/login", response_model=UserOut)
async def login(body: LoginIn, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    ip = _client_ip(request)
    now = time.time()
    _FAILS[ip] = [t for t in _FAILS[ip] if now - t < _WINDOW]
    if len(_FAILS[ip]) >= 10:
        raise HTTPException(429, "Too many attempts")

    user = await db.scalar(select(User).where(func.lower(User.username) == body.username.strip().lower()))
    if not verify_password(body.password, user.password_hash if user else None) or user is None:
        _FAILS[ip].append(now)
        raise HTTPException(401, "Invalid username or password")

    _FAILS.pop(ip, None)
    await create_session(db, response, user.id)
    return user


@router.post("/auth/logout", status_code=204)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    await destroy_session(db, request, response)


@router.get("/auth/me", response_model=MeOut)
async def me(user: User | None = Depends(optional_user)):
    # 200 with null instead of 401 keeps the browser console clean
    return {"user": user}


@router.get("/users", response_model=list[UserOut])
async def users(_: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(User).order_by(User.id))).all()
