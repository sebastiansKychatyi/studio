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
from .models import (
    Alarm, Board, BoardColumn, CalEvent, Card, Client, ClientLog, Expense, Invoice, PushLater, PushSent, PushSubscription, Recurring, StudyWork, Subject,
    TelegramLink, TimeEntry, User, UserSettings,
)
from .routers.study import current_semester, has_class
from .sync import utcnow

log = logging.getLogger("push")

LANGS = ("sk", "cs", "uk", "en")
TEXT = {
    "sk": {
        "alarm": "Budík", "snooze": "Odložiť o 10 min", "stop": "Vypnúť", "reminder": "Pripomienka", "due": "Dnes je termín",
        "mention": "Spomenuli vás", "assign": "Pridelené vám", "bill": "Platba na dnes", "variable": "suma sa mení",
        "test": "Testovacie upozornenie", "testBody": "Upozornenia fungujú.",
        "today": "Dnes", "tomorrow": "Zajtra", "free": "Voľný deň", "first": "prvé",
        "events": ("udalosť", "udalosti", "udalostí"), "deadlines": ("termín", "termíny", "termínov"), "bills": ("platba", "platby", "platieb"),
    },
    "cs": {
        "alarm": "Budík", "snooze": "Odložit o 10 min", "stop": "Vypnout", "reminder": "Připomínka", "due": "Dnes je termín",
        "mention": "Zmínili vás", "assign": "Přiděleno vám", "bill": "Platba na dnes", "variable": "částka se mění",
        "test": "Testovací oznámení", "testBody": "Oznámení fungují.",
        "today": "Dnes", "tomorrow": "Zítra", "free": "Volný den", "first": "první",
        "events": ("událost", "události", "událostí"), "deadlines": ("termín", "termíny", "termínů"), "bills": ("platba", "platby", "plateb"),
    },
    "uk": {
        "alarm": "Будильник", "snooze": "Відкласти на 10 хв", "stop": "Вимкнути", "reminder": "Нагадування", "due": "Сьогодні дедлайн",
        "mention": "Вас згадали", "assign": "Вам призначено", "bill": "Сьогодні оплата", "variable": "сума змінюється",
        "test": "Тестове сповіщення", "testBody": "Сповіщення працюють.",
        "today": "Сьогодні", "tomorrow": "Завтра", "free": "Вільний день", "first": "перше",
        "events": ("подія", "події", "подій"), "deadlines": ("дедлайн", "дедлайни", "дедлайнів"), "bills": ("платіж", "платежі", "платежів"),
    },
    "en": {
        "alarm": "Alarm", "snooze": "Snooze 10 min", "stop": "Turn off", "reminder": "Reminder", "due": "Due today",
        "mention": "You were mentioned", "assign": "Assigned to you", "bill": "Payment due today", "variable": "amount varies",
        "test": "Test notification", "testBody": "Notifications work.",
        "today": "Today", "tomorrow": "Tomorrow", "free": "Free day", "first": "first",
        "events": ("event", "events", "events"), "deadlines": ("deadline", "deadlines", "deadlines"), "bills": ("payment", "payments", "payments"),
    },
}
# Kinds a user can switch off in settings ("notify" key); alarms ignore quiet hours
KINDS = ("alarms", "events", "due", "mentions", "assign", "bills", "summary", "evening", "classes", "study", "clients", "invoices", "timer")
# CRM and timer texts, per language
CRM = {
    "sk": {"followup": "Ozvať sa", "due": "Splatnosť faktúry dnes", "late": "Faktúra po splatnosti", "timer": "Časovač stále beží", "running": "beží {h} h"},
    "cs": {"followup": "Ozvat se", "due": "Splatnost faktury dnes", "late": "Faktura po splatnosti", "timer": "Časovač stále běží", "running": "běží {h} h"},
    "uk": {"followup": "Зв’язатися", "due": "Сьогодні термін оплати", "late": "Рахунок прострочено", "timer": "Таймер досі йде", "running": "іде {h} год"},
    "en": {"followup": "Get in touch", "due": "Invoice due today", "late": "Invoice overdue", "timer": "Timer still running", "running": "running for {h} h"},
}
# Kinds of study works and of classes, per language
STUDY = {
    "sk": {"assignment": "Zadanie", "project": "Semestrálna práca", "exam": "Skúška", "credit": "Zápočet", "lecture": "Prednáška", "seminar": "Cvičenie", "lab": "Laboratórium", "in": "o {n} dni", "in1": "zajtra", "in0": "dnes"},
    "cs": {"assignment": "Úkol", "project": "Semestrální práce", "exam": "Zkouška", "credit": "Zápočet", "lecture": "Přednáška", "seminar": "Cvičení", "lab": "Laboratoř", "in": "za {n} dny", "in1": "zítra", "in0": "dnes"},
    "uk": {"assignment": "Завдання", "project": "Курсова", "exam": "Іспит", "credit": "Залік", "lecture": "Лекція", "seminar": "Семінар", "lab": "Лабораторна", "in": "через {n} дні", "in1": "завтра", "in0": "сьогодні"},
    "en": {"assignment": "Assignment", "project": "Coursework", "exam": "Exam", "credit": "Credit test", "lecture": "Lecture", "seminar": "Seminar", "lab": "Lab", "in": "in {n} days", "in1": "tomorrow", "in0": "today"},
}

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


def channels_on() -> bool:
    """Web Push or the Telegram bot is set up."""
    from . import telegram

    return enabled() or telegram.configured()


async def send(db: AsyncSession, user_id: int, kind: str, build: Builder, ttl: int = 3600) -> int:
    """Push to every device of the user and to their Telegram chat, if their settings allow it. Returns how many were reached."""
    from . import telegram

    if not channels_on():
        return 0
    prefs = await prefs_of(db, user_id)
    if kind in KINDS and (prefs.get("notify") or {}).get(kind) is False:
        return 0
    if kind not in ("alarms", "test") and _quiet(prefs, datetime.now(tz_of(prefs))):
        return 0
    chat = await telegram.chat_of(db, user_id) if telegram.configured() and (prefs.get("notify") or {}).get("telegram") is not False else None
    subs = (await db.scalars(select(PushSubscription).where(PushSubscription.user_id == user_id))).all() if enabled() else []
    if not subs and chat is None:
        return 0
    lang = lang_of(prefs)
    payload = build(TEXT[lang], lang)
    reached = await telegram.notify(chat, payload, lang, kind) if chat is not None else 0
    if not subs:
        return reached
    urgency = "high" if kind in ("alarms", "events", "test") else "normal"
    results = await asyncio.gather(*(asyncio.to_thread(_post, s, payload, ttl, urgency) for s in subs))
    # Uninstalled app / revoked permission: the push service says the endpoint is gone
    gone = [s.id for s, r in zip(subs, results) if r in (404, 410)]
    if gone:
        await db.execute(delete(PushSubscription).where(PushSubscription.id.in_(gone)))
        await db.commit()
    return reached + sum(r is None for r in results)


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


def occurs(e: CalEvent, day: date) -> bool:
    """Does the event happen on this day (weekly repeats, end date, skipped days)."""
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
            if not occurs(e, day):
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


async def _classes(db: AsyncSession, uid: int, local: datetime) -> None:
    """Reminder `remind` minutes before each class (setting of the semester)."""
    sem = await current_semester(db, uid)
    if sem is None or sem.remind is None:
        return
    at = local + timedelta(minutes=sem.remind)
    for s in (await db.scalars(select(Subject).where(Subject.semester_id == sem.id))).all():
        for x in s.lessons:
            if x.start != f"{at:%H:%M}" or not has_class(x, sem, at.date()) or not await _once(db, f"c{x.id}:{at.date()}"):
                continue
            await send(db, uid, "classes", lambda t, lang, s=s, x=x: {
                "title": f"{STUDY[lang][x.kind]}: {s.name}", "body": " · ".join(filter(None, [f"{x.start}–{x.end}", x.room or s.room, s.teacher])),
                "tag": f"class-{x.id}", "url": f"/{lang}/panel/study",
            }, ttl=1800)


async def _works(db: AsyncSession, uid: int, local: datetime) -> None:
    """Study deadlines 3 days before, 1 day before and on the day (09:00)."""
    today = local.date()
    for w in (await db.scalars(select(StudyWork).where(StudyWork.user_id == uid, StudyWork.status != "done", StudyWork.due >= today, StudyWork.due <= today + timedelta(days=3)))).all():
        n = (w.due - today).days
        if n == 2 or not await _once(db, f"w{w.id}:{n}"):
            continue
        s = await db.get(Subject, w.subject_id) if w.subject_id else None
        await send(db, uid, "study", lambda t, lang, w=w, s=s, n=n: {
            "title": f"{STUDY[lang][w.kind]}: {w.title}"[:120],
            "body": " · ".join(filter(None, [STUDY[lang][f'in{n}'] if n < 2 else STUDY[lang]['in'].format(n=n), w.due_time, s.name if s else ""])),
            "tag": f"work-{w.id}", "url": f"/{lang}/panel/study",
        })


async def _clients(db: AsyncSession, uid: int, local: datetime) -> None:
    """09:00: follow-ups due today, invoices due today and the day after they become overdue."""
    today = local.date()
    names = dict((await db.execute(select(Client.id, Client.name).where(Client.user_id == uid))).all())
    for x in (await db.scalars(select(ClientLog).where(ClientLog.user_id == uid, ClientLog.followup == today, ClientLog.followup_done.is_(False)))).all():
        if await _once(db, f"f{x.id}"):
            await send(db, uid, "clients", lambda t, lang, x=x: {
                "title": f"{CRM[lang]['followup']}: {names.get(x.client_id, '')}", "body": x.text[:200], "tag": f"followup-{x.id}",
                "url": f"/{lang}/panel/clients?id={x.client_id}",
            })
    for i in (await db.scalars(select(Invoice).where(Invoice.user_id == uid, Invoice.paid_on.is_(None), Invoice.due.in_([today, today - timedelta(days=1)])))).all():
        late = i.due < today
        if await _once(db, f"i{i.id}:{'late' if late else 'due'}"):
            await send(db, uid, "invoices", lambda t, lang, i=i, late=late: {
                "title": f"{CRM[lang]['late' if late else 'due']}: {names.get(i.client_id, '')}",
                "body": f"{i.number} {i.title} · {i.amount:.2f} {i.currency}".strip(), "tag": f"invoice-{i.id}",
                "url": f"/{lang}/panel/clients?id={i.client_id}",
            })


async def _timer(db: AsyncSession, uid: int, now: datetime, prefs: dict) -> None:
    """A timer running for more than N hours (settings, default 4) was probably forgotten."""
    hours = int((prefs.get("notify") or {}).get("timerHours") or 4)
    t = await db.scalar(select(TimeEntry).where(TimeEntry.user_id == uid, TimeEntry.end.is_(None)))
    if t is None:
        return
    start = t.start if t.start.tzinfo else t.start.replace(tzinfo=now.tzinfo)
    if now - start >= timedelta(hours=hours) and await _once(db, f"t{t.id}"):
        await send(db, uid, "timer", lambda tx, lang: {
            "title": CRM[lang]["timer"], "body": " · ".join(filter(None, [CRM[lang]["running"].format(h=hours), t.note])), "tag": "timer",
            "url": f"/{lang}/panel/time",
        })


def plural(lang: str, n: int, forms: tuple[str, str, str]) -> str:
    if lang == "en":
        i = 0 if n == 1 else 1
    elif lang == "uk":
        i = 0 if n % 10 == 1 and n % 100 != 11 else 1 if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else 2
    else:  # sk, cs
        i = 0 if n == 1 else 1 if 2 <= n <= 4 else 2
    return f"{n} {forms[i]}"


async def _summary(db: AsyncSession, uid: int, local: datetime, evening: bool) -> None:
    """One push with the day: "3 events, 2 deadlines, 1 payment; first — 10:00 Lecture"."""
    from .routers.today import build_today  # avoids an import cycle

    day = local.date() + timedelta(days=1 if evening else 0)
    if not await _once(db, f"{'v' if evening else 's'}{uid}:{day}"):
        return
    user = await db.get(User, uid)
    t = await build_today(db, user, day)
    deadlines = len(t.tasks.overdue) + len(t.tasks.today) + sum(w.due <= day for w in t.study)
    # Classes count as events; the first item is whatever starts first
    plan = sorted([(e.start, e.title) for e in t.events] + [(c.start, c.subject) for c in t.classes])

    def build(texts: dict, lang: str) -> dict:
        parts = [plural(lang, n, texts[key]) for n, key in ((len(plan), "events"), (deadlines, "deadlines"), (len(t.money.bills), "bills")) if n]
        body = ", ".join(parts) or texts["free"]
        if plan:
            body += f"; {texts['first']} — {plan[0][0]} {plan[0][1]}"
        return {
            "title": f"{texts['tomorrow' if evening else 'today']} · {day:%d.%m.}", "body": body[:220], "tag": f"summary-{day}",
            "url": f"/{lang}/panel/today" + (f"?date={day}" if evening else ""),
        }

    await send(db, uid, "evening" if evening else "summary", build)


async def tick(now: datetime) -> None:
    async with SessionLocal() as db:
        for job in (await db.scalars(select(PushLater).where(PushLater.fire_at <= now))).all():
            payload = json.loads(job.payload)
            await db.delete(job)
            await db.commit()
            await send(db, job.user_id, "alarms", lambda t, lang, p=payload: p, ttl=900)
        # Users with a device or a Telegram chat
        uids = set((await db.scalars(select(PushSubscription.user_id).distinct())).all())
        uids |= set((await db.scalars(select(TelegramLink.user_id).where(TelegramLink.chat_id.is_not(None)))).all())
        for uid in sorted(uids):
            prefs = await prefs_of(db, uid)
            local = now.astimezone(tz_of(prefs))
            await _alarms(db, uid, local)
            await _events(db, uid, local)
            await _classes(db, uid, local)
            await _timer(db, uid, now, prefs)
            hm, n = f"{local:%H:%M}", prefs.get("notify") or {}
            if hm == "09:00":
                await _due(db, uid, local)
                await _bills(db, uid, local)
                await _works(db, uid, local)
                await _clients(db, uid, local)
            # Morning summary (on by default) and "what is tomorrow" (off by default)
            if n.get("summary") is not False and hm == (n.get("summaryAt") or "07:30"):
                await _summary(db, uid, local, evening=False)
            if n.get("evening") and hm == (n.get("eveningAt") or "20:00"):
                await _summary(db, uid, local, evening=True)
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
