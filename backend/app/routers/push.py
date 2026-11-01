import json
from datetime import timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import notify
from ..config import settings
from ..db import get_db
from ..models import PushLater, PushSubscription, User
from ..schemas import PushKeyOut, SnoozeCancelIn, SnoozeIn, SubscriptionIn, UnsubscribeIn
from ..security import current_user
from ..sync import utcnow

# Web Push subscriptions of the installed app / browser (one per device)
router = APIRouter(prefix="/push", tags=["push"])


@router.get("/key", response_model=PushKeyOut)
async def key(_: User = Depends(current_user)):
    return PushKeyOut(key=settings.vapid_public_key, enabled=notify.enabled())


@router.post("/subscribe", status_code=204)
async def subscribe(body: SubscriptionIn, request: Request, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    sub = await db.scalar(select(PushSubscription).where(PushSubscription.endpoint == body.endpoint))
    if sub is None:
        sub = PushSubscription(endpoint=body.endpoint)
        db.add(sub)
    # Same device, maybe another account now
    sub.user_id, sub.p256dh, sub.auth = user.id, body.keys.p256dh, body.keys.auth
    sub.user_agent = request.headers.get("user-agent", "")[:300]
    await db.commit()


@router.post("/unsubscribe", status_code=204)
async def unsubscribe(body: UnsubscribeIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(PushSubscription).where(PushSubscription.endpoint == body.endpoint, PushSubscription.user_id == user.id))
    await db.commit()


@router.post("/test")
async def test(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> dict:
    """Sends a notification to every device of the user; returns how many were reached."""
    sent = await notify.send(db, user.id, "test", lambda t, lang: {"title": t["test"], "body": t["testBody"], "tag": "test", "url": f"/{lang}/panel/settings"})
    return {"sent": sent}


@router.post("/snooze", status_code=204)
async def snooze(body: SnoozeIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Snooze button of an alarm notification: the same alarm again in a few minutes."""
    prefs = await notify.prefs_of(db, user.id)
    lang = notify.lang_of(prefs)
    payload = notify.alarm_payload(notify.TEXT[lang], lang, body.alarm_id, body.time, body.label)
    if body.tag:
        payload["tag"] = body.tag
    db.add(PushLater(user_id=user.id, fire_at=utcnow() + timedelta(minutes=body.minutes), payload=json.dumps(payload, ensure_ascii=False)))
    await db.commit()


@router.post("/snooze/cancel", status_code=204)
async def cancel_snooze(body: SnoozeCancelIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Snooze cancelled in the app: drop the pending push with that tag."""
    for job in (await db.scalars(select(PushLater).where(PushLater.user_id == user.id))).all():
        if json.loads(job.payload).get("tag") == body.tag:
            await db.delete(job)
    await db.commit()
