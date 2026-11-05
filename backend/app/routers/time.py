import json
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Card, Client, Invoice, Project, TimeEntry, User
from ..notify import prefs_of, tz_of
from ..schemas import InvoiceOut, ReportRow, TimeIn, TimeInvoiceIn, TimeOut, TimePatch, TimeReport, TimeStartIn, TimeStopIn
from ..security import current_user
from ..sync import check_offline, utcnow
from ..crm import own_client
from .clients import invoice_out, local_today, next_number

# Time tracking (personal): one running timer, manual entries, report, invoice from tracked time.
# The start time lives on the server, so the timer keeps counting while the app is closed.
router = APIRouter(prefix="/time", tags=["time"])


def _aware(d: datetime) -> datetime:
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


async def _links(db: AsyncSession, user: User, body) -> None:
    """Card → its client / project when not given; all links must be the user's own."""
    if body.card_id is not None:
        card = await db.get(Card, body.card_id)
        if card is None:
            raise HTTPException(404, "Card not found")
        body.client_id = body.client_id or card.client_id
        body.project_id = body.project_id or card.project_id
    if body.project_id is not None and body.client_id is None:
        p = await db.get(Project, body.project_id)
        body.client_id = p.client_id if p else None
    await own_client(db, user, body.client_id, body.project_id)


async def _running(db: AsyncSession, user: User) -> TimeEntry | None:
    return await db.scalar(select(TimeEntry).where(TimeEntry.user_id == user.id, TimeEntry.end.is_(None)))


async def _entry(db: AsyncSession, entry_id: int, user: User) -> TimeEntry:
    t = await db.get(TimeEntry, entry_id)
    if t is None or t.user_id != user.id:
        raise HTTPException(404, "Entry not found")
    return t


@router.get("/running", response_model=TimeOut | None)
async def running(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await _running(db, user)


@router.post("/start", response_model=TimeOut, status_code=201)
async def start(body: TimeStartIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Starts the timer; a running one is stopped at that moment (only one runs)."""
    await _links(db, user, body)
    at = _aware(body.start) if body.start else utcnow()
    if (cur := await _running(db, user)) is not None:
        cur.end = max(at, _aware(cur.start))
    t = TimeEntry(user_id=user.id, client_id=body.client_id, project_id=body.project_id, card_id=body.card_id, note=body.note.strip(), start=at)
    db.add(t)
    await db.commit()
    return t


@router.post("/stop", response_model=TimeOut | None)
async def stop(body: TimeStopIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    cur = await _running(db, user)
    if cur is None:
        return None  # already stopped (e.g. on another device)
    cur.end = max(_aware(body.end) if body.end else utcnow(), _aware(cur.start))
    await db.commit()
    return cur


@router.get("", response_model=list[TimeOut])
async def entries(
    start: date = Query(alias="from"), end: date = Query(alias="to"), user: User = Depends(current_user), db: AsyncSession = Depends(get_db)
):
    tz = tz_of(await prefs_of(db, user.id))
    a = datetime(start.year, start.month, start.day, tzinfo=tz)
    b = datetime(end.year, end.month, end.day, tzinfo=tz) + timedelta(days=1)
    q = select(TimeEntry).where(TimeEntry.user_id == user.id, TimeEntry.start >= a, TimeEntry.start < b).order_by(TimeEntry.start.desc())
    return (await db.scalars(q)).all()


@router.post("", response_model=TimeOut, status_code=201)
async def add(body: TimeIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Time entered by hand."""
    if body.end <= body.start:
        raise HTTPException(422, "End must be after start")
    await _links(db, user, body)
    t = TimeEntry(user_id=user.id, **body.model_dump())
    t.note = t.note.strip()
    db.add(t)
    await db.commit()
    return t


@router.patch("/{entry_id}", response_model=TimeOut)
async def update(entry_id: int, body: TimePatch, request: Request, response: Response, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    t = await _entry(db, entry_id, user)
    check_offline(request, response, t.updated_at)
    sent = body.model_fields_set
    for field in sent:
        setattr(t, field, getattr(body, field) if field in ("client_id", "project_id", "card_id", "end") or getattr(body, field) is not None else getattr(t, field))
    await own_client(db, user, t.client_id, t.project_id)
    if t.end is not None and _aware(t.end) <= _aware(t.start):
        raise HTTPException(422, "End must be after start")
    await db.commit()
    return t


@router.delete("/{entry_id}", status_code=204)
async def delete(entry_id: int, request: Request, response: Response, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    t = await _entry(db, entry_id, user)
    check_offline(request, response, t.updated_at)
    await db.delete(t)
    await db.commit()


def _minutes(t: TimeEntry, now: datetime) -> int:
    return max(int(((_aware(t.end) if t.end else now) - _aware(t.start)).total_seconds() // 60), 0)


async def _report(db: AsyncSession, user: User, start: date, end: date, client_id: int | None, project_id: int | None, unbilled: bool = False):
    tz = tz_of(await prefs_of(db, user.id))
    a = datetime(start.year, start.month, start.day, tzinfo=tz)
    b = datetime(end.year, end.month, end.day, tzinfo=tz) + timedelta(days=1)
    q = select(TimeEntry).where(TimeEntry.user_id == user.id, TimeEntry.start >= a, TimeEntry.start < b)
    if client_id is not None:
        q = q.where(TimeEntry.client_id == client_id)
    if project_id is not None:
        q = q.where(TimeEntry.project_id == project_id)
    if unbilled:
        q = q.where(TimeEntry.invoice_id.is_(None), TimeEntry.end.isnot(None))
    entries = (await db.scalars(q)).all()
    now = utcnow()
    groups: dict[tuple, list[TimeEntry]] = defaultdict(list)
    for t in entries:
        groups[(t.client_id, t.project_id, t.card_id, "" if t.card_id else t.note)].append(t)
    rows = []
    for (cid, pid, card_id, note), items in groups.items():
        client = await db.get(Client, cid) if cid else None
        project = await db.get(Project, pid) if pid else None
        card = await db.get(Card, card_id) if card_id else None
        rate = project.rate if project and project.rate is not None else client.rate if client else None
        minutes = sum(_minutes(t, now) for t in items)
        amount = round(float(rate) * minutes / 60, 2) if rate is not None else None
        title = card.title if card else note or (project.title if project else "")
        rows.append(ReportRow(client_id=cid, project_id=pid, card_id=card_id, title=title, minutes=minutes, rate=float(rate) if rate is not None else None,
                              amount=amount, currency=client.currency if client else "EUR"))
    rows.sort(key=lambda r: -r.minutes)
    return rows, entries


@router.get("/report", response_model=TimeReport)
async def report(
    start: date = Query(alias="from"),
    end: date = Query(alias="to"),
    client_id: int | None = Query(None, alias="client"),
    project_id: int | None = Query(None, alias="project"),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    """Period × client / project → minutes and amount by rate, grouped by task."""
    rows, entries = await _report(db, user, start, end, client_id, project_id)
    amounts: dict[str, float] = defaultdict(float)
    for r in rows:
        if r.amount is not None:
            amounts[r.currency] += r.amount
    now = utcnow()
    return TimeReport(
        rows=rows, minutes=sum(r.minutes for r in rows), amounts={k: round(v, 2) for k, v in amounts.items()},
        unbilled_minutes=sum(_minutes(t, now) for t in entries if t.invoice_id is None and t.end is not None),
    )


@router.post("/invoice", response_model=InvoiceOut, status_code=201)
async def invoice_from_time(body: TimeInvoiceIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Invoice from unbilled tracked time of a client (one line per task); it becomes an expected payment in the CRM."""
    await own_client(db, user, body.client_id, body.project_id)
    client = await db.get(Client, body.client_id)
    rows, entries = await _report(db, user, body.start, body.end, body.client_id, body.project_id, unbilled=True)
    if not rows:
        raise HTTPException(409, "No unbilled time in this period")
    if any(r.rate is None for r in rows):
        raise HTTPException(422, "Set an hourly rate for the client or the project")
    prefs = await prefs_of(db, user.id)
    settings = prefs.get("invoice") or {}
    issued = await local_today(db, user)
    items = [{"title": r.title or "—", "hours": round(r.minutes / 60, 2), "rate": r.rate, "amount": r.amount} for r in rows]
    inv = Invoice(
        user_id=user.id, client_id=client.id, project_id=body.project_id,
        number=await next_number(db, user, str(settings.get("prefix") or ""), issued),
        title=body.title.strip() or f"{body.start:%d.%m.%Y} – {body.end:%d.%m.%Y}",
        amount=round(sum(x["amount"] for x in items), 2), currency=client.currency, issued=issued,
        due=issued + timedelta(days=int(settings.get("dueDays") or 14)), items=json.dumps(items, ensure_ascii=False),
    )
    db.add(inv)
    await db.flush()
    for t in entries:
        t.invoice_id = inv.id
    await db.commit()
    return invoice_out(inv, issued)
