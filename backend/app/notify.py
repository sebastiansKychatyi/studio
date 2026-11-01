"""Web Push: sending to all devices of a user and the minute scheduler.

Scheduled: alarms, calendar reminders, today's deadlines (09:00), monthly payments due (09:00),
alarms snoozed from a notification. Immediate (kanban router): @mentions and assignments.
Runs inside the API process (a single uvicorn process). Every sent occurrence is written to
push_sent, so a restart within the same minute does not send it twice.
Times are the user's local time (settings key "tz", set by the panel).
"""

import asyncio
import json
import logging
import math
import re
from collections.abc import Callable
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from pywebpush import WebPushException, webpush
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import SessionLocal
from .models import Alarm, Board, BoardColumn, CalEvent, Card, Expense, PushLater, PushSent, PushSubscription, Recurring, User, UserSettings
from .sync import utcnow

log = logging.getLogger("push")

LANGS = ("sk", "cs", "uk", "en")
TEXT = {
    "sk": {
        "alarm": "Budík", "snooze": "Odložiť o 10 min", "stop": "Vypnúť", "reminder": "Pripomienka", "due": "Dnes je termín",
        "mention": "Spomenuli vás", "assign": "Pridelené vám", "bill": "Platba na dnes", "variable": "suma sa mení",
        "test": "Testovacie upozornenie", "testBody": "Upozornenia fungujú.",
    },
    "cs": {
        "alarm": "Budík", "snooze": "Odložit o 10 min", "stop": "Vypnout", "reminder": "Připomínka", "due": "Dnes je termín",
        "mention": "Zmínili vás", "assign": "Přiděleno vám", "bill": "Platba na dnes", "variable": "částka se mění",
        "test": "Testovací oznámení", "testBody": "Oznámení fungují.",
    },
    "uk": {
        "alarm": "Будильник", "snooze": "Відкласти на 10 хв", "stop": "Вимкнути", "reminder": "Нагадування", "due": "Сьогодні дедлайн",
        "mention": "Вас згадали", "assign": "Вам призначено", "bill": "Сьогодні оплата", "variable": "сума змінюється",
        "test": "Тестове сповіщення", "testBody": "Сповіщення працюють.",
    },
    "en": {
        "alarm": "Alarm", "snooze": "Snooze 10 min", "stop": "Turn off", "reminder": "Reminder", "due": "Due today",
        "mention": "You were mentioned", "assign": "Assigned to you", "bill": "Payment due today", "variable": "amount varies",
        "test": "Test notification", "testBody": "Notifications work.",
    },
}
# Kinds a user can switch off in settings ("notify" key); alarms ignore quiet hours
KINDS = ("alarms", "events", "due", "mentions", "assign", "bills")

Builder = Callable[[dict, str], dict]  # (texts, lang) -> payload for the service worker


def enabled() -> bool:
    return bool(settings.vapid_public_key and settings.vapid_private_key)


async def prefs_of(db: AsyncSession, user_id: int) -> dict:
    row = await db.get(UserSettings, user_id)
    try:
        data = json.loads(row.data) if row else {}
    except ValueError:
        data = {}
    return data if isinstance(data, dict) else {}


def tz_of(prefs: dict) -> ZoneInfo:
    try:
        return ZoneInfo(str(prefs.get("tz") or settings.default_tz))
    except (ValueError, KeyError):
        return ZoneInfo(settings.default_tz)


def lang_of(prefs: dict) -> str:
    lang = prefs.get("lang")
    return lang if lang in LANGS else LANGS[0]


def _quiet(prefs: dict, local: datetime) -> bool:
    n = prefs.get("notify") or {}
    if not n.get("quiet"):
        return False
    start, end, hm = str(n.get("quietFrom") or "22:00"), str(n.get("quietTo") or "07:00"), f"{local:%H:%M}"
    return start <= hm < end if start <= end else (hm >= start or hm < end)


def _post(sub: PushSubscription, payload: dict, ttl: int, urgency: str) -> int | None:
    """Blocking send. None = delivered to the push service, else HTTP status (0 = no answer)."""
    try:
        webpush(
            {"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}},
            data=json.dumps(payload, ensure_ascii=False),
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={"sub": settings.vapid_subject},
            ttl=ttl,
            headers={"Urgency": urgency},
            timeout=10,
        )
    except WebPushException as e:
        return e.response.status_code if e.response is not None else 0
    except Exception:  # noqa: BLE001 - network problems must not stop the scheduler
        log.exception("push failed")
        return 0
    return None


async def send(db: AsyncSession, user_id: int, kind: str, build: Builder, ttl: int = 3600) -> int:
    """Push to every device of the user if their settings allow it. Returns devices reached."""
    if not enabled():
        return 0
    prefs = await prefs_of(db, user_id)
    if kind in KINDS and (prefs.get("notify") or {}).get(kind) is False:
        return 0
    if kind not in ("alarms", "test") and _quiet(prefs, datetime.now(tz_of(prefs))):
        return 0
    subs = (await db.scalars(select(PushSubscription).where(PushSubscription.user_id == user_id))).all()
    if not subs:
        return 0
    lang = lang_of(prefs)
    payload = build(TEXT[lang], lang)
    urgency = "high" if kind in ("alarms", "events", "test") else "normal"
    results = await asyncio.gather(*(asyncio.to_thread(_post, s, payload, ttl, urgency) for s in subs))
    # Uninstalled app / revoked permission: the push service says the endpoint is gone
    gone = [s.id for s, r in zip(subs, results) if r in (404, 410)]
    if gone:
        await db.execute(delete(PushSubscription).where(PushSubscription.id.in_(gone)))
        await db.commit()
    return sum(r is None for r in results)


def alarm_payload(t: dict, lang: str, alarm_id: int, time: str, label: str) -> dict:
    return {
        "title": f"⏰ {time}",
        "body": label or t["alarm"],
        "tag": f"alarm-{alarm_id}",
        "url": f"/{lang}/panel/alarms",
        "alarm": {"id": alarm_id, "time": time, "label": label},
        "actions": [{"action": "snooze", "title": t["snooze"]}, {"action": "stop", "title": t["stop"]}],
        "requireInteraction": True,
        "vibrate": [400, 150, 400, 150, 400, 150, 800],
    }


async def _once(db: AsyncSession, key: str) -> bool:
    """True the first time a scheduled occurrence is seen."""
    if await db.get(PushSent, key):
        return False
    db.add(PushSent(key=key))
    await db.commit()
    return True


def _occurs(e: CalEvent, day: date) -> bool:
    if e.repeat != "weekly":
        return e.date == day
    days = {int(d) for d in e.days.split(",") if d}
    return day >= e.date and (e.until is None or day <= e.until) and (day.weekday() + 1) % 7 in days and day.isoformat() not in e.skip


async def _alarms(db: AsyncSession, uid: int, local: datetime) -> None:
    hm, today = f"{local:%H:%M}", local.date()
    for a in (await db.scalars(select(Alarm).where(Alarm.user_id == uid, Alarm.enabled, Alarm.time == hm))).all():
        days = [int(d) for d in a.days.split(",") if d]
        if days and (today.weekday() + 1) % 7 not in days:
            continue
        if not await _once(db, f"a{a.id}:{today}:{hm}"):
            continue
        await send(db, uid, "alarms", lambda t, lang, a=a: alarm_payload(t, lang, a.id, a.time, a.label), ttl=900)
        if not days:  # one-time alarm switches itself off (as in the open panel)
            a.enabled = False
            await db.commit()


async def _events(db: AsyncSession, uid: int, local: datetime) -> None:
    for e in (await db.scalars(select(CalEvent).where(CalEvent.user_id == uid, CalEvent.remind.isnot(None)))).all():
        # The occurrence may be up to `remind` minutes ahead, also on a later day
        for k in range(math.ceil(e.remind / 1440) + 2):
            day = local.date() + timedelta(days=k)
            if not _occurs(e, day):
                continue
            h, m = map(int, e.start.split(":"))
            start = datetime(day.year, day.month, day.day, h, m, tzinfo=local.tzinfo)
            if start - timedelta(minutes=e.remind) != local or not await _once(db, f"e{e.id}:{day}:{e.start}:{e.remind}"):
                continue
            when = f"{e.start}–{e.end}" + (f" · {day:%d.%m.}" if k else "")
            await send(
                db, uid, "events",
                lambda t, lang, e=e, day=day, when=when: {
                    "title": f"{t['reminder']}: {e.title}", "body": when, "tag": f"event-{e.id}-{day}",
                    "url": f"/{lang}/panel/calendar?date={day}&event={e.id}",
                },
            )


async def _due(db: AsyncSession, uid: int, local: datetime) -> None:
    """Open cards due today that are the user's (assigned, or own and unassigned)."""
    today = local.date()
    rows = (await db.execute(
        select(Card, BoardColumn.board_id).join(BoardColumn).where(
            Card.due_date == today, (Card.assignee_id == uid) | (Card.assignee_id.is_(None) & (Card.created_by == uid))
        )
    )).all()
    cards = []
    for card, board_id in rows:
        last = await db.scalar(select(BoardColumn.id).where(BoardColumn.board_id == board_id).order_by(BoardColumn.position.desc()).limit(1))
        if card.column_id != last:
            cards.append((card, board_id))
    if not cards or not await _once(db, f"d{uid}:{today}"):
        return
    first, board_id = cards[0]
    await send(db, uid, "due", lambda t, lang: {
        "title": t["due"], "body": " · ".join(c.title for c, _ in cards)[:200], "tag": f"due-{today}",
        "url": f"/{lang}/panel?board={board_id}&card={first.id}",
    })


async def _bills(db: AsyncSession, uid: int, local: datetime) -> None:
    """Monthly expense templates due today and not paid yet this month."""
    today = local.date()
    start = today.replace(day=1)
    month_end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    for tpl in (await db.scalars(select(Recurring).where(Recurring.user_id == uid, Recurring.kind == "expenses"))).all():
        if min(tpl.day, month_end.day) != today.day:
            continue
        paid = await db.scalar(select(func.count()).select_from(Expense).where(Expense.recurring_id == tpl.id, Expense.spent_on >= start, Expense.spent_on <= month_end))
        if paid or not await _once(db, f"b{tpl.id}:{start:%Y-%m}"):
            continue
        await send(db, uid, "bills", lambda t, lang, tpl=tpl: {
            "title": f"{t['bill']}: {tpl.title}", "body": f"{tpl.amount:.2f} {tpl.currency}" if tpl.amount else t["variable"],
            "tag": f"bill-{tpl.id}", "url": f"/{lang}/panel/expenses",
        })


async def tick(now: datetime) -> None:
    async with SessionLocal() as db:
        for job in (await db.scalars(select(PushLater).where(PushLater.fire_at <= now))).all():
            payload = json.loads(job.payload)
            await db.delete(job)
            await db.commit()
            await send(db, job.user_id, "alarms", lambda t, lang, p=payload: p, ttl=900)
        for uid in (await db.scalars(select(PushSubscription.user_id).distinct())).all():
            prefs = await prefs_of(db, uid)
            local = now.astimezone(tz_of(prefs))
            await _alarms(db, uid, local)
            await _events(db, uid, local)
            if f"{local:%H:%M}" == "09:00":
                await _due(db, uid, local)
                await _bills(db, uid, local)
        if now.minute == 0:
            await db.execute(delete(PushSent).where(PushSent.sent_at < now - timedelta(days=3)))
            await db.commit()


async def run_scheduler() -> None:
    """Checks every 20 s, acts once per minute."""
    last = None
    while True:
        minute = utcnow().replace(second=0, microsecond=0)
        if minute != last:
            last = minute
            try:
                await tick(minute)
            except Exception:  # noqa: BLE001 - keep the loop alive
                log.exception("push scheduler")
        await asyncio.sleep(20)


# Kanban: @mentions and assignments, sent right after the change
MENTION = re.compile(r"@([\w.-]+)")


async def card_changed(card_id: int, actor_id: int, before: tuple[str, int | None] | None) -> None:
    """before = (title + description, assignee) before the change; None for a new card."""
    if not enabled():
        return
    async with SessionLocal() as db:
        card = await db.get(Card, card_id)
        if card is None:
            return
        board = await db.get(Board, (await db.get(BoardColumn, card.column_id)).board_id)
        people = {board.created_by, *board.member_ids} - {None}
        # Who can see the card: a private one only its author
        sees = {card.created_by} if card.is_private else people or {card.created_by}
        actor = await db.get(User, actor_id)
        who = actor.name or actor.username if actor else ""

        def build(kind: str):
            return lambda t, lang: {
                "title": f"{t[kind]}: {card.title}"[:120], "body": f"{who} · {board.title}", "tag": f"card-{card.id}",
                "url": f"/{lang}/panel?board={board.id}&card={card.id}",
            }

        notified = set()
        if card.assignee_id and card.assignee_id != actor_id and card.assignee_id in sees and (before is None or before[1] != card.assignee_id):
            await send(db, card.assignee_id, "assign", build("assign"))
            notified.add(card.assignee_id)
        old = {m.lower() for m in MENTION.findall(before[0])} if before else set()
        new = {m.lower() for m in MENTION.findall(f"{card.title}\n{card.description}")} - old
        if new:
            for u in (await db.scalars(select(User).where(func.lower(User.username).in_(new)))).all():
                if u.id != actor_id and u.id in sees and u.id not in notified:
                    await send(db, u.id, "mentions", build("mention"))
