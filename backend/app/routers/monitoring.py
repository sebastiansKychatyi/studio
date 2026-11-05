import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import monitoring as mon
from ..config import settings
from ..db import SessionLocal, get_db
from ..mailer import configured as smtp_configured, send_mail
from ..models import MonitorEnv, MonitorError, MonitorEvent, MonitorProject, MonitorSettings, User
from ..schemas import (
    MonitorEnvIn,
    MonitorEnvOut,
    MonitorEnvPatch,
    MonitorErrorOut,
    MonitorEventOut,
    MonitorProjectIn,
    MonitorProjectOut,
    MonitorProjectPatch,
    MonitorSettingsIn,
    MonitorSettingsOut,
)
from ..security import current_user

# Project monitoring in the panel (admins only) + the webhook the projects call.
# Tokens and webhook secrets stay on the server: they are never returned.
router = APIRouter(prefix="/monitoring", tags=["monitoring"])


def is_admin(user: User) -> bool:
    names = {x.strip().lower() for x in settings.monitoring_admins.split(",") if x.strip()}
    return not names or user.username.lower() in names


async def admin(user: User = Depends(current_user)) -> User:
    if not is_admin(user):
        raise HTTPException(403, "Monitoring is for admins")
    return user


def _out(e: MonitorEnv) -> MonitorEnvOut:
    try:
        snapshot = json.loads(e.snapshot) if e.snapshot else None
    except ValueError:
        snapshot = None
    return MonitorEnvOut(
        id=e.id, project_id=e.project_id, name=e.name, kind=e.kind, base_url=e.base_url, enabled=e.enabled,
        poll_interval_seconds=e.poll_interval_seconds, has_token=bool(e.api_token), has_webhook=bool(e.webhook_secret),
        state=e.state, status=e.status, fail_count=e.fail_count, last_poll_at=e.last_poll_at, last_ok_at=e.last_ok_at,
        last_error=e.last_error, down_since=e.down_since, degraded_since=e.degraded_since, token_invalid=e.token_invalid, snapshot=snapshot,
    )


async def _project(db: AsyncSession, project_id: int) -> MonitorProject:
    p = await db.get(MonitorProject, project_id)
    if p is None:
        raise HTTPException(404, "Project not found")
    return p


async def _project_out(db: AsyncSession, p: MonitorProject) -> MonitorProjectOut:
    envs = (await db.scalars(select(MonitorEnv).where(MonitorEnv.project_id == p.id).order_by(MonitorEnv.id))).all()
    return MonitorProjectOut(id=p.id, name=p.name, description=p.description, enabled=p.enabled, envs=[_out(e) for e in envs])


async def _env(db: AsyncSession, env_id: int) -> MonitorEnv:
    e = await db.get(MonitorEnv, env_id)
    if e is None:
        raise HTTPException(404, "Environment not found")
    return e


async def _name_free(db: AsyncSession, project_id: int, name: str) -> None:
    if await db.scalar(select(MonitorEnv.id).where(MonitorEnv.project_id == project_id, MonitorEnv.name == name)):
        raise HTTPException(409, "Name already used")


@router.get("/access")
async def access(user: User = Depends(current_user)) -> dict:
    """Whether the panel shows the Monitoring item."""
    return {"allowed": is_admin(user)}


# ===== Projects =====
@router.get("/projects", response_model=list[MonitorProjectOut])
async def list_projects(_: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    return [await _project_out(db, p) for p in (await db.scalars(select(MonitorProject).order_by(MonitorProject.id))).all()]


@router.post("/projects", response_model=MonitorProjectOut, status_code=201)
async def create_project(body: MonitorProjectIn, _: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    if await db.scalar(select(MonitorProject.id).where(MonitorProject.name == body.name)):
        raise HTTPException(409, "Name already used")
    p = MonitorProject(**body.model_dump())
    db.add(p)
    await db.commit()
    return await _project_out(db, p)


@router.patch("/projects/{project_id}", response_model=MonitorProjectOut)
async def update_project(project_id: int, body: MonitorProjectPatch, _: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    p = await _project(db, project_id)
    if body.name and body.name != p.name:
        if await db.scalar(select(MonitorProject.id).where(MonitorProject.name == body.name)):
            raise HTTPException(409, "Name already used")
        p.name = body.name
    if body.description is not None:
        p.description = body.description
    if body.enabled is not None:
        p.enabled = body.enabled
    await db.commit()
    return await _project_out(db, p)


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: int, _: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    p = await _project(db, project_id)
    env_ids = select(MonitorEnv.id).where(MonitorEnv.project_id == p.id)
    # Explicit, so SQLite (no FK cascade) is cleaned up too
    await db.execute(delete(MonitorEvent).where(MonitorEvent.env_id.in_(env_ids)))
    await db.execute(delete(MonitorError).where(MonitorError.env_id.in_(env_ids)))
    await db.execute(delete(MonitorEnv).where(MonitorEnv.project_id == p.id))
    await db.delete(p)
    await db.commit()


# ===== Environments =====
@router.post("/envs", response_model=MonitorEnvOut, status_code=201)
async def create_env(body: MonitorEnvIn, _: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    await _project(db, body.project_id)
    await _name_free(db, body.project_id, body.name)
    data = body.model_dump()
    data["enabled"] = body.enabled and bool(body.api_token)  # no token = nothing to poll with
    data["api_token"], data["webhook_secret"] = mon.seal(body.api_token), mon.seal(body.webhook_secret)
    e = MonitorEnv(**data)
    db.add(e)
    await db.commit()
    return _out(e)


@router.patch("/envs/{env_id}", response_model=MonitorEnvOut)
async def update_env(env_id: int, body: MonitorEnvPatch, _: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    e = await _env(db, env_id)
    if body.name and body.name != e.name:
        await _name_free(db, e.project_id, body.name)
        e.name = body.name
    if body.kind:
        e.kind = body.kind
    if body.base_url:
        e.base_url = body.base_url
    if body.api_token:  # a new token: maybe the 401 is fixed now
        e.api_token, e.token_invalid = mon.seal(body.api_token), False
    if body.webhook_secret:
        e.webhook_secret = mon.seal(body.webhook_secret)
    elif body.clear_webhook:
        e.webhook_secret = ""
    if body.poll_interval_seconds:
        e.poll_interval_seconds = body.poll_interval_seconds
    if body.enabled is not None:
        if body.enabled and not e.api_token:
            raise HTTPException(400, "Set the API token first")
        e.enabled = body.enabled
    await db.commit()
    return _out(e)


@router.delete("/envs/{env_id}", status_code=204)
async def delete_env(env_id: int, _: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    e = await _env(db, env_id)
    await db.execute(delete(MonitorEvent).where(MonitorEvent.env_id == e.id))
    await db.execute(delete(MonitorError).where(MonitorError.env_id == e.id))
    await db.delete(e)
    await db.commit()


@router.post("/envs/{env_id}/check", response_model=MonitorEnvOut)
async def check_now(env_id: int, _: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    """Poll /status and /errors right away (the "Check now" button)."""
    e = await _env(db, env_id)
    if not e.api_token:
        raise HTTPException(400, "Set the API token first")
    await mon.poll_status(db, e)
    if not e.token_invalid:
        await mon.poll_errors(db, e)
    return _out(e)


@router.get("/envs/{env_id}/events", response_model=list[MonitorEventOut])
async def events(env_id: int, limit: int = Query(50, ge=1, le=500), _: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    await _env(db, env_id)
    q = select(MonitorEvent).where(MonitorEvent.env_id == env_id).order_by(MonitorEvent.at.desc(), MonitorEvent.id.desc()).limit(limit)
    return (await db.scalars(q)).all()


@router.get("/errors", response_model=list[MonitorErrorOut])
async def errors(
    project_id: int | None = Query(None, alias="project"),
    env_id: int | None = Query(None, alias="env"),
    source: str | None = None,
    open_only: bool = Query(False, alias="open"),
    limit: int = Query(200, ge=1, le=1000),
    _: User = Depends(admin),
    db: AsyncSession = Depends(get_db),
):
    q = select(MonitorError)
    if project_id is not None:
        q = q.where(MonitorError.env_id.in_(select(MonitorEnv.id).where(MonitorEnv.project_id == project_id)))
    if env_id is not None:
        q = q.where(MonitorError.env_id == env_id)
    if source:
        q = q.where(MonitorError.source == source)
    if open_only:
        q = q.where(MonitorError.resolved.is_(False))
    return (await db.scalars(q.order_by(MonitorError.last_seen_at.desc().nulls_last(), MonitorError.id.desc()).limit(limit))).all()


@router.get("/envs/{env_id}/logs")
async def logs(
    env_id: int,
    service: str = Query("backend", min_length=1, max_length=60, pattern=r"^[A-Za-z0-9_.-]+$"),
    tail: int = Query(300, ge=10, le=2000),
    q: str = Query("", max_length=200),
    _: User = Depends(admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Asked by the server (the token never reaches the browser)."""
    e = await _env(db, env_id)
    res = await asyncio.to_thread(mon.fetch, mon.endpoint(e, "logs", service=service, tail=tail, q=q), mon.unseal(e.api_token))
    if res.code != 200 or not isinstance(res.body, dict):
        raise HTTPException(502, res.error or f"The project answered {res.code}")
    return {"service": res.body.get("service", service), "origin": res.body.get("origin"), "lines": res.body.get("lines") or []}


# ===== Settings =====
@router.get("/settings", response_model=MonitorSettingsOut)
async def get_settings(_: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(MonitorSettings, 1)
    return MonitorSettingsOut(
        recipients=row.recipients if row else "", default_recipients=settings.monitoring_alert_emails, smtp=smtp_configured(),
        encrypted=bool(settings.monitoring_secret_key), errors_interval=settings.monitoring_errors_interval,
    )


@router.put("/settings", response_model=MonitorSettingsOut)
async def save_settings(body: MonitorSettingsIn, user: User = Depends(admin), db: AsyncSession = Depends(get_db)):
    row = await db.get(MonitorSettings, 1)
    if row is None:
        row = MonitorSettings(id=1, seeded=True)
        db.add(row)
    row.recipients = body.recipients.strip()
    await db.commit()
    return await get_settings(user, db)


@router.post("/test-mail")
async def test_mail(_: User = Depends(admin), db: AsyncSession = Depends(get_db)) -> dict:
    to = await mon.recipients(db)
    ok = await send_mail(to, "[monitoring] тестовое письмо", "Почта мониторинга проектов работает.")
    return {"sent": ok, "to": to, "smtp": smtp_configured()}


# ===== Webhook =====
async def _handle_webhook(env_id: int, payload: dict) -> None:
    """Background part of the webhook: store the error and e-mail it (30 min limit per error)."""
    async with SessionLocal() as db:
        env = await db.get(MonitorEnv, env_id)
        event = payload.get("event") or {}
        if env is None or not isinstance(event, dict) or "id" not in event:
            return
        db.add(MonitorEvent(env_id=env.id, kind="webhook", text=f"error #{event.get('id')} ({event.get('reason')}): {str(event.get('message') or '')[:200]}"))
        await mon.save_errors(db, env, [event], "webhook", mail=True, reasons={int(event["id"]): str(event.get("reason") or "")})


@router.post("/webhook/{env_id}")
async def webhook(env_id: int, request: Request, background: BackgroundTasks, db: AsyncSession = Depends(get_db)) -> dict:
    """Called by a project (its MONITORING_WEBHOOK_URL). Signature over the raw body with this env's secret; answers fast."""
    raw = await request.body()
    env = await db.get(MonitorEnv, env_id)
    if env is None or not mon.valid_signature(mon.unseal(env.webhook_secret), raw, request.headers.get("x-drivebook-signature")):
        raise HTTPException(401, "Bad signature")
    try:
        payload = json.loads(raw)
    except ValueError:
        raise HTTPException(400, "Invalid JSON") from None
    if payload.get("type") == "test":
        mon.log.info("webhook test for env %s", env_id)
        db.add(MonitorEvent(env_id=env.id, kind="webhook", text="test webhook received"))
        await db.commit()
    elif payload.get("type") == "error":
        background.add_task(_handle_webhook, env.id, payload)
    return {"ok": True}
