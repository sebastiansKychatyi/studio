"""Project monitoring: polls the monitoring API of every enabled environment (/status, /errors) by the
shared contract (e-Drivebook is the first project), keeps its state (up / degraded / down / off) and
sends one e-mail per state change.

Decisions are plain functions over the environment row (apply_status, changed_errors, next_cursor,
mail_due, valid_signature) so they are tested without network or database; the rest is glue.
A server that is down sends nothing itself: "not answering" is detected here by polling /status.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import SessionLocal
from .mailer import send_mail
from .models import MonitorEnv, MonitorError, MonitorEvent, MonitorProject, MonitorSettings
from .sync import utcnow

log = logging.getLogger("monitoring")

FAILS_TO_DOWN = 3  # failed polls in a row (network, timeout, 5xx)
DEGRADED_ALERT_AFTER = timedelta(minutes=10)
ERROR_ALERT_EVERY = timedelta(minutes=30)  # at most one e-mail per error group
TIMEOUT = 10  # seconds per request
STATUSES = ("ok", "degraded", "down")

# First project, added once (tokens are filled in the panel; until then the environments stay off)
SEED = {
    "name": "e-Drivebook",
    "description": "Driving school booking (FastAPI + Nuxt)",
    "envs": [
        {"name": "e-drivebook.com", "kind": "production", "base_url": "https://e-drivebook.com/v1/monitoring/external"},
        {"name": "k2drive.com", "kind": "test", "base_url": "https://k2drive.com/v1/monitoring/external"},
    ],
}


@dataclass
class Response:
    code: int  # HTTP status; 0 = no answer (network error, timeout)
    body: Any = None
    error: str = ""


@dataclass
class Mail:
    subject: str
    text: str


# ===== Secrets at rest =====
def _fernet():
    if not settings.monitoring_secret_key:
        return None
    from cryptography.fernet import Fernet  # comes with pywebpush

    return Fernet(settings.monitoring_secret_key.encode())


def seal(plain: str) -> str:
    """Value for the DB: encrypted with MONITORING_SECRET_KEY when it is set."""
    f = _fernet()
    return f"enc:{f.encrypt(plain.encode()).decode()}" if plain and f else plain


def unseal(stored: str) -> str:
    if not stored.startswith("enc:"):
        return stored
    try:
        f = _fernet()
        return f.decrypt(stored[4:].encode()).decode() if f else ""
    except Exception:  # noqa: BLE001 - key changed: the value has to be entered again
        log.error("monitoring secret cannot be decrypted (MONITORING_SECRET_KEY changed?)")
        return ""


# ===== HTTP =====
def fetch(url: str, token: str) -> Response:
    """Blocking GET with the Bearer token (run in a thread). Tests replace it."""
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json", "User-Agent": "duo-studio-monitor"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read()
            try:
                return Response(r.status, json.loads(raw or b"null"))
            except ValueError:
                return Response(r.status, None, "Invalid JSON in the answer")
    except urllib.error.HTTPError as e:
        return Response(e.code, None, f"HTTP {e.code} {e.reason}")
    except Exception as e:  # noqa: BLE001 - every failure is a failed poll
        return Response(0, None, f"{type(e).__name__}: {e}")


Fetcher = Callable[[str, str], Response]


def endpoint(env: MonitorEnv, path: str, **query) -> str:
    q = urllib.parse.urlencode({k: v for k, v in query.items() if v not in (None, "")})
    return f"{env.base_url.rstrip('/')}/{path}" + (f"?{q}" if q else "")


# ===== Decisions =====
def _aware(d: datetime | None) -> datetime | None:
    return d.replace(tzinfo=timezone.utc) if d is not None and d.tzinfo is None else d


def duration(td: timedelta) -> str:
    minutes = int(td.total_seconds() // 60)
    h, m = divmod(minutes, 60)
    d, h = divmod(h, 24)
    return " ".join(p for p in (f"{d} д" if d else "", f"{h} ч" if h else "", f"{m} мин") if p)


def _problems(body: dict) -> list[str]:
    """Failed checks and scheduler jobs that are stale or failed, as text lines."""
    lines = [f"check {name}: {c.get('detail') or 'not ok'}" for name, c in (body.get("checks") or {}).items() if isinstance(c, dict) and not c.get("ok")]
    for job in (body.get("scheduler") or {}).get("jobs") or []:
        if job.get("stale") or job.get("last_status") == "error":
            why = "stale" if job.get("stale") else "error"
            lines.append(f"job {job.get('name') or job.get('id')} ({why}): {job.get('last_error') or ''}".rstrip(": "))
    errors = body.get("errors") or {}
    if errors.get("last_1h"):
        lines.append(f"errors: {errors.get('last_1h')} за час, {errors.get('open', 0)} открытых")
    return lines


def valid_status(body: Any) -> bool:
    """Required for every project: status, time, checks; the rest is optional."""
    return isinstance(body, dict) and body.get("status") in STATUSES and bool(body.get("time")) and isinstance(body.get("checks"), dict)


def _set_state(env: MonitorEnv, state: str, events: list[str]) -> None:
    if env.state != state:
        events.append(f"{env.state} → {state}")
        env.state = state


def apply_status(env: MonitorEnv, res: Response, now: datetime, title: str = "") -> tuple[list[Mail], list[str]]:
    """New state after one /status poll; returns e-mails to send and history lines. title = "Project · env"."""
    title = title or env.name
    mails: list[Mail] = []
    events: list[str] = []
    env.last_poll_at = now

    if res.code == 401:
        # Wrong token: tell once, but the server answers, so it is not "down"
        env.last_error = "401: неверный токен"
        if not env.token_invalid:
            env.token_invalid = True
            events.append("401: invalid token")
            mails.append(Mail(f"[{title}] неверный токен мониторинга", (
                f"Мониторинг {title} ({env.base_url}) получил 401 Unauthorized.\n"
                "Проверьте api_token окружения в панели (Мониторинг → Настройки) и токен мониторинга на стороне проекта."
            )))
        env.fail_count = 0
        return mails, events
    env.token_invalid = False

    def recovered() -> None:
        if env.state == "down":
            since = _aware(env.down_since) or now
            mails.append(Mail(f"[{title}] снова работает", (
                f"{title} ({env.base_url}) снова отвечает.\nПростой: {duration(now - since)} (с {since:%d.%m.%Y %H:%M} UTC)."
            )))
            env.down_since = None

    if res.code == 404:
        # The monitoring API is turned off over there; the server itself answers
        recovered()
        env.fail_count = 0
        env.last_error = "404: API мониторинга выключен на стороне проекта"
        _set_state(env, "off", events)
        return mails, events

    if res.code != 200 or not valid_status(res.body):
        env.fail_count += 1
        env.last_error = res.error or (f"HTTP {res.code}" if res.code != 200 else "Invalid answer: status, time and checks are required")
        if env.fail_count >= FAILS_TO_DOWN and env.state != "down":
            _go_down(env, now, title, mails, events)
        return mails, events

    body = res.body
    env.fail_count = 0
    env.last_ok_at = now
    env.snapshot = json.dumps(body, ensure_ascii=False)
    env.status = body["status"]

    if env.status == "down":
        env.last_error = "; ".join(_problems(body)) or "status: down"
        if env.state != "down":
            _go_down(env, now, title, mails, events)
        return mails, events

    recovered()
    env.last_error = ""
    if env.status == "degraded":
        if env.state != "degraded":
            env.degraded_since, env.degraded_alerted = now, False
        _set_state(env, "degraded", events)
        since = _aware(env.degraded_since) or now
        if not env.degraded_alerted and now - since >= DEGRADED_ALERT_AFTER:
            env.degraded_alerted = True
            mails.append(Mail(f"[{title}] работает с проблемами (degraded)", (
                f"{title} в состоянии degraded уже {duration(now - since)}.\n\n" + "\n".join(_problems(body) or ["(подробностей нет)"])
            )))
    else:
        env.degraded_since, env.degraded_alerted = None, False
        _set_state(env, "up", events)
    return mails, events


def _go_down(env: MonitorEnv, now: datetime, title: str, mails: list[Mail], events: list[str]) -> None:
    env.down_since = now
    _set_state(env, "down", events)
    lines = [f"{title} ({env.base_url}) не работает с {now:%d.%m.%Y %H:%M} UTC.", f"Последняя ошибка: {env.last_error or '—'}"]
    if (last_ok := _aware(env.last_ok_at)) is not None:
        lines.append(f"Последний успешный опрос: {last_ok:%d.%m.%Y %H:%M} UTC")
    mails.append(Mail(f"[{title}] НЕ ОТВЕЧАЕТ", "\n".join(lines)))


def changed_errors(known: dict[int, int], items: list[dict]) -> list[dict]:
    """Error groups that are new or whose count grew (dedup by env, id, count). known = {remote id: count}."""
    out = []
    for e in items:
        if not isinstance(e, dict) or "id" not in e:
            continue
        rid, count = int(e["id"]), int(e.get("count") or 1)
        if rid not in known or count > known[rid]:
            out.append(e)
            known[rid] = count
    return out


def parse_time(s: Any) -> datetime | None:
    try:
        return _aware(datetime.fromisoformat(str(s).replace("Z", "+00:00")))
    except ValueError:
        return None


def next_cursor(cursor: str, items: list[dict]) -> str:
    """since for the next /errors call: the newest last_seen_at seen so far."""
    best, best_raw = parse_time(cursor) if cursor else None, cursor
    for e in items:
        t = parse_time(e.get("last_seen_at")) if isinstance(e, dict) else None
        if t and (best is None or t > best):
            best, best_raw = t, str(e["last_seen_at"])
    return best_raw


def mail_due(mailed_at: datetime | None, now: datetime) -> bool:
    return mailed_at is None or now - _aware(mailed_at) >= ERROR_ALERT_EVERY


def valid_signature(secret: str, raw: bytes, header: str | None) -> bool:
    """X-Drivebook-Signature: sha256=<hex HMAC-SHA256(secret, raw body)>, compared in constant time."""
    if not secret or not header:
        return False
    expected = "sha256=" + hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.strip())


def error_mail(title: str, e: dict, reason: str = "") -> Mail:
    where = " ".join(x for x in (e.get("method"), e.get("path")) if x)
    head = [
        f"Окружение: {title}",
        f"Источник: {e.get('source')} · {e.get('level')}" + (f" · {e.get('logger_name')}" if e.get("logger_name") else ""),
        f"Запрос: {where}" if where else "",
        f"Повторов: {e.get('count')} · впервые {e.get('first_seen_at')} · последний раз {e.get('last_seen_at')}",
        f"Причина: {reason}" if reason else "",
    ]
    body = [str(e.get("message") or ""), str(e.get("traceback") or "")]
    text = "\n".join(x for x in head if x) + "\n\n" + "\n\n".join(x for x in body if x)
    return Mail(f"[{title}] ошибка: {str(e.get('message') or '')[:90]}", text.strip())


# ===== Database + e-mail glue =====
async def seed(db: AsyncSession) -> None:
    """Adds the first project once (deleting it later does not bring it back)."""
    row = await db.get(MonitorSettings, 1)
    if row is not None and row.seeded:
        return
    if row is None:
        row = MonitorSettings(id=1, recipients="")
        db.add(row)
    row.seeded = True
    if not await db.scalar(select(MonitorProject).where(MonitorProject.name == SEED["name"])):
        project = MonitorProject(name=SEED["name"], description=SEED["description"])
        db.add(project)
        await db.flush()
        for e in SEED["envs"]:
            db.add(MonitorEnv(project_id=project.id, enabled=False, **e))
    await db.commit()


async def title_of(db: AsyncSession, env: MonitorEnv) -> str:
    project = await db.get(MonitorProject, env.project_id)
    return f"{project.name} · {env.name}" if project else env.name


async def recipients(db: AsyncSession) -> list[str]:
    row = await db.get(MonitorSettings, 1)
    raw = (row.recipients if row and row.recipients.strip() else settings.monitoring_alert_emails)
    return [x.strip() for x in raw.replace(";", ",").split(",") if x.strip()]


async def _notify(db: AsyncSession, env: MonitorEnv, mails: list[Mail]) -> None:
    to = await recipients(db)
    for m in mails:
        sent = await send_mail(to, m.subject, m.text)
        db.add(MonitorEvent(env_id=env.id, kind="mail", text=f"{'sent' if sent else 'NOT sent (SMTP)'}: {m.subject}"))
    await db.commit()


async def poll_status(db: AsyncSession, env: MonitorEnv, fetcher: Fetcher = fetch) -> None:
    res = await asyncio.to_thread(fetcher, endpoint(env, "status"), unseal(env.api_token))
    mails, events = apply_status(env, res, utcnow(), await title_of(db, env))
    for text in events:
        db.add(MonitorEvent(env_id=env.id, kind="state", text=text + (f" · {env.last_error}" if env.last_error else "")))
    await db.commit()
    await _notify(db, env, mails)


async def save_errors(db: AsyncSession, env: MonitorEnv, items: list[dict], via: str, mail: bool, reasons: dict[int, str] | None = None) -> int:
    """Stores new / grown error groups; e-mails them (at most once per 30 min each) when `mail`."""
    rows = {r.remote_id: r for r in (await db.scalars(select(MonitorError).where(MonitorError.env_id == env.id))).all()}
    changed = changed_errors({rid: r.count for rid, r in rows.items()}, items)
    now = utcnow()
    title = await title_of(db, env)
    mails = []
    for e in changed:
        rid = int(e["id"])
        row = rows.get(rid) or MonitorError(env_id=env.id, remote_id=rid, via=via)
        if rid not in rows:
            db.add(row)
            rows[rid] = row
        row.source, row.level = str(e.get("source") or "")[:20], str(e.get("level") or "")[:20]
        row.logger_name, row.message = str(e.get("logger_name") or "")[:200], str(e.get("message") or "")
        row.traceback, row.path = str(e.get("traceback") or ""), str(e.get("path") or "")[:500]
        row.method, row.user_id = str(e.get("method") or "")[:10], e.get("user_id")
        row.count, row.resolved = int(e.get("count") or 1), bool(e.get("resolved"))
        row.first_seen_at, row.last_seen_at = parse_time(e.get("first_seen_at")), parse_time(e.get("last_seen_at"))
        if mail and not row.resolved and mail_due(row.mailed_at, now):
            row.mailed_at = now
            mails.append(error_mail(title, e, (reasons or {}).get(rid, "")))
    await db.commit()
    await _notify(db, env, mails)
    return len(changed)


async def poll_errors(db: AsyncSession, env: MonitorEnv, fetcher: Fetcher = fetch) -> int:
    url = endpoint(env, "errors", since=env.errors_cursor or None, state="all", limit=200)
    res = await asyncio.to_thread(fetcher, url, unseal(env.api_token))
    env.errors_polled_at = utcnow()
    if res.code != 200 or not isinstance(res.body, list):
        await db.commit()
        return 0
    # With a webhook the e-mail comes from it; polling is only the safety net then
    n = await save_errors(db, env, res.body, "poll", mail=not env.webhook_secret)
    env.errors_cursor = next_cursor(env.errors_cursor, res.body)
    await db.commit()
    return n


def _due(last: datetime | None, every: int, now: datetime) -> bool:
    return last is None or now - _aware(last) >= timedelta(seconds=every)


async def tick(fetcher: Fetcher = fetch) -> None:
    now = utcnow()
    async with SessionLocal() as db:
        q = (select(MonitorEnv.id).join(MonitorProject, MonitorProject.id == MonitorEnv.project_id)
             .where(MonitorEnv.enabled, MonitorProject.enabled, MonitorEnv.api_token != ""))
        ids = (await db.scalars(q)).all()

    # Environments in parallel, each in its own session
    async def one(env_id: int) -> None:
        async with SessionLocal() as db:
            env = await db.get(MonitorEnv, env_id)
            if env is None:
                return
            if _due(env.last_poll_at, env.poll_interval_seconds, now):
                await poll_status(db, env, fetcher)
            if _due(env.errors_polled_at, settings.monitoring_errors_interval, now) and not env.token_invalid:
                await poll_errors(db, env, fetcher)
    await asyncio.gather(*(one(i) for i in ids), return_exceptions=True)


async def run_monitor() -> None:
    """Checks every 15 s which environment is due (poll_interval_seconds of each)."""
    while True:
        try:
            await tick()
        except Exception:  # noqa: BLE001 - keep the loop alive
            log.exception("monitoring tick")
        await asyncio.sleep(15)
