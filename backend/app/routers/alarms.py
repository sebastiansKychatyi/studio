from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Alarm, User
from ..schemas import AlarmIn, AlarmOut, AlarmPatch
from ..security import current_user

# Alarms are personal; ringing happens in the browser
router = APIRouter(tags=["alarms"])


def _out(a: Alarm) -> AlarmOut:
    return AlarmOut(id=a.id, time=a.time, label=a.label, days=[int(d) for d in a.days.split(",") if d], enabled=a.enabled)


async def _own(db: AsyncSession, alarm_id: int, user: User) -> Alarm:
    alarm = await db.get(Alarm, alarm_id)
    if alarm is None or alarm.user_id != user.id:
        raise HTTPException(404, "Alarm not found")
    return alarm


@router.get("/alarms", response_model=list[AlarmOut])
async def list_alarms(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(select(Alarm).where(Alarm.user_id == user.id).order_by(Alarm.time, Alarm.id))
    return [_out(a) for a in rows]


@router.post("/alarms", response_model=AlarmOut, status_code=201)
async def create_alarm(body: AlarmIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    alarm = Alarm(
        user_id=user.id, time=body.time, label=body.label.strip(), days=",".join(map(str, body.days)), enabled=body.enabled
    )
    db.add(alarm)
    await db.commit()
    return _out(alarm)


@router.patch("/alarms/{alarm_id}", response_model=AlarmOut)
async def update_alarm(alarm_id: int, body: AlarmPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    alarm = await _own(db, alarm_id, user)
    if body.time is not None:
        alarm.time = body.time
    if body.label is not None:
        alarm.label = body.label.strip()
    if body.days is not None:
        alarm.days = ",".join(map(str, body.days))
    if body.enabled is not None:
        alarm.enabled = body.enabled
    await db.commit()
    return _out(alarm)


@router.delete("/alarms/{alarm_id}", status_code=204)
async def delete_alarm(alarm_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.delete(await _own(db, alarm_id, user))
    await db.commit()
