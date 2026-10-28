import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import User, UserSettings
from ..schemas import SettingsIn
from ..security import current_user

# Per-account UI settings (theme, kanban layout, currency, open boards…), merged key by key
router = APIRouter(tags=["settings"])
MAX_BYTES = 20_000


async def _load(db: AsyncSession, user: User) -> tuple[UserSettings, dict]:
    row = await db.get(UserSettings, user.id)
    if row is None:
        row = UserSettings(user_id=user.id, data="{}")
        db.add(row)
    try:
        data = json.loads(row.data or "{}")
    except ValueError:
        data = {}
    return row, data if isinstance(data, dict) else {}


@router.get("/me/settings")
async def get_settings(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> dict:
    return (await _load(db, user))[1]


@router.patch("/me/settings")
async def update_settings(body: SettingsIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> dict:
    """Merge keys; a null value removes the key."""
    row, data = await _load(db, user)
    for key, value in body.data.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = value
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    if len(raw.encode()) > MAX_BYTES:
        raise HTTPException(413, "Settings too large")
    row.data = raw
    await db.commit()
    return data
