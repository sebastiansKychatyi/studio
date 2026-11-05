import json
from datetime import date, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..crm import own_client
from ..db import get_db
from ..models import Board, BoardColumn, CalEvent, Client, ClientLog, Income, Invoice, Project, TimeEntry, User
from ..notify import occurs, prefs_of, tz_of
from ..schemas import (
    ClientDetail,
    ClientIn,
    ClientListItem,
    ClientLogIn,
    ClientLogOut,
    ClientLogPatch,
    ClientOut,
    ClientPatch,
    InvoiceIn,
    InvoiceOut,
    InvoicePatch,
    MeetingOut,
    OpenCard,
    PayInvoiceIn,
    ProjectIn,
    ProjectOut,
    ProjectPatch,
)
from ..security import current_user
from .kanban import can_see_board, can_see_card
from .money import _convert

# Mini CRM (personal): clients, their projects, contact history, invoices (expected payments).
# Cards, events, income and tracked time can point to a client / project.
router = APIRouter(tags=["clients"])


async def _client(db: AsyncSession, client_id: int, user: User) -> Client:
    c = await db.get(Client, client_id)
    if c is None or c.user_id != user.id:
        raise HTTPException(404, "Client not found")
    return c


async def _own(db: AsyncSession, model, item_id: int, user: User):
    row = await db.get(model, item_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(404, "Not found")
    return row


def _client_out(c: Client) -> ClientOut:
    return ClientOut.model_validate(c).model_copy(update={"tags": [t for t in c.tags.split(",") if t]})


def invoice_out(i: Invoice, today: date) -> InvoiceOut:
    status = "paid" if i.paid_on else "overdue" if i.due < today else "pending"
    return InvoiceOut.model_validate(i).model_copy(update={"status": status, "items": json.loads(i.items or "[]")})


async def next_number(db: AsyncSession, user: User, prefix: str, day: date) -> str:
    """Invoice number: prefix + year + running number of that year, e.g. 2026003."""
    n = await db.scalar(select(func.count()).select_from(Invoice).where(Invoice.user_id == user.id, Invoice.issued >= day.replace(month=1, day=1)))
    return f"{prefix}{day.year}{(n or 0) + 1:03d}"


async def local_today(db: AsyncSession, user: User) -> date:
    return datetime.now(tz_of(await prefs_of(db, user.id))).date()


# Clients
@router.get("/clients", response_model=list[ClientListItem])
async def list_clients(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    today = await local_today(db, user)
    owed = dict((await db.execute(
        select(Invoice.client_id, func.count()).where(Invoice.user_id == user.id, Invoice.paid_on.is_(None)).group_by(Invoice.client_id)
    )).all())
    late = dict((await db.execute(
        select(Invoice.client_id, func.count()).where(Invoice.user_id == user.id, Invoice.paid_on.is_(None), Invoice.due < today).group_by(Invoice.client_id)
    )).all())
    rows = (await db.scalars(select(Client).where(Client.user_id == user.id).order_by(func.lower(Client.name)))).all()
    return [ClientListItem(**_client_out(c).model_dump(), open_invoices=owed.get(c.id, 0), late_invoices=late.get(c.id, 0)) for c in rows]


@router.post("/clients", response_model=ClientOut, status_code=201)
async def create_client(body: ClientIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    data = body.model_dump()
    data["tags"] = ",".join(t.strip() for t in body.tags if t.strip())
    c = Client(user_id=user.id, **data)
    db.add(c)
    await db.commit()
    return _client_out(c)


@router.patch("/clients/{client_id}", response_model=ClientOut)
async def update_client(client_id: int, body: ClientPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    c = await _client(db, client_id, user)
    for field in body.model_fields_set:
        value = getattr(body, field)
        if field == "tags":
            c.tags = ",".join(t.strip() for t in value or [] if t.strip())
        elif field == "rate" or value is not None:
            setattr(c, field, value)
    await db.commit()
    return _client_out(c)


@router.delete("/clients/{client_id}", status_code=204)
async def delete_client(client_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.delete(await _client(db, client_id, user))
    await db.commit()


@router.get("/clients/{client_id}", response_model=ClientDetail)
async def client_detail(client_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Everything about one client: projects, history, invoices, open tasks, coming meetings, money and hours."""
    c = await _client(db, client_id, user)
    today = await local_today(db, user)
    projects = (await db.scalars(select(Project).where(Project.client_id == c.id).order_by(Project.status, Project.id.desc()))).all()
    log = (await db.scalars(select(ClientLog).where(ClientLog.client_id == c.id).order_by(ClientLog.day.desc(), ClientLog.id.desc()))).all()
    invoices = (await db.scalars(select(Invoice).where(Invoice.client_id == c.id).order_by(Invoice.issued.desc(), Invoice.id.desc()))).all()

    # Open cards linked to the client (not in a board's last column)
    cards = []
    boards = (await db.scalars(select(Board).options(selectinload(Board.columns).selectinload(BoardColumn.cards)))).all()
    for b in boards:
        if not can_see_board(b, user) or not b.columns:
            continue
        for col in b.columns[:-1]:
            for card in col.cards:
                if card.client_id == c.id and can_see_card(card, user):
                    cards.append(OpenCard(id=card.id, title=card.title, due_date=card.due_date, board_id=b.id, board_title=b.title, column_title=col.title))

    # Next occurrences of meetings with the client (60 days)
    meetings = []
    for e in (await db.scalars(select(CalEvent).where(CalEvent.user_id == user.id, CalEvent.client_id == c.id))).all():
        for k in range(60):
            day = today + timedelta(days=k)
            if occurs(e, day):
                meetings.append(MeetingOut(id=e.id, title=e.title, date=day, start=e.start, end=e.end))
                break
    meetings.sort(key=lambda m: (m.date, m.start))

    # Income in EUR (all time / this month) and tracked hours
    earned = lambda since=None: db.scalar(  # noqa: E731
        select(func.coalesce(func.sum(Income.amount), 0)).where(Income.user_id == user.id, Income.client_id == c.id, *([Income.spent_on >= since] if since else []))
    )
    month = today.replace(day=1)
    entries = (await db.scalars(select(TimeEntry).where(TimeEntry.user_id == user.id, TimeEntry.client_id == c.id))).all()
    now = datetime.now(tz_of(await prefs_of(db, user.id)))
    minutes = lambda since=None: sum(  # noqa: E731
        int(((t.end or now) - t.start).total_seconds() // 60) for t in entries if since is None or t.start.date() >= since
    )
    return ClientDetail(
        client=_client_out(c),
        projects=[ProjectOut.model_validate(p) for p in projects],
        log=[ClientLogOut.model_validate(x) for x in log],
        invoices=[invoice_out(i, today) for i in invoices],
        cards=cards,
        meetings=meetings[:10],
        earned_total=float(await earned()),
        earned_month=float(await earned(month)),
        minutes_total=minutes(),
        minutes_month=minutes(month),
    )


# Projects
@router.get("/projects", response_model=list[ProjectOut])
async def list_projects(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """All projects of all clients (pickers on cards, timer, income)."""
    return (await db.scalars(select(Project).where(Project.user_id == user.id).order_by(Project.status, func.lower(Project.title)))).all()


@router.post("/clients/{client_id}/projects", response_model=ProjectOut, status_code=201)
async def create_project(client_id: int, body: ProjectIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await _client(db, client_id, user)
    p = Project(user_id=user.id, client_id=client_id, **body.model_dump())
    db.add(p)
    await db.commit()
    return p


@router.patch("/projects/{project_id}", response_model=ProjectOut)
async def update_project(project_id: int, body: ProjectPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    p = await _own(db, Project, project_id, user)
    for field in body.model_fields_set:
        value = getattr(body, field)
        if field in ("budget", "rate", "start", "end") or value is not None:
            setattr(p, field, value)
    await db.commit()
    return p


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.delete(await _own(db, Project, project_id, user))
    await db.commit()


# Contact history
@router.post("/clients/{client_id}/log", response_model=ClientLogOut, status_code=201)
async def add_log(client_id: int, body: ClientLogIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await _client(db, client_id, user)
    x = ClientLog(user_id=user.id, client_id=client_id, **body.model_dump())
    db.add(x)
    await db.commit()
    return x


@router.patch("/client-log/{log_id}", response_model=ClientLogOut)
async def update_log(log_id: int, body: ClientLogPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    x = await _own(db, ClientLog, log_id, user)
    for field in body.model_fields_set:
        value = getattr(body, field)
        if field == "followup" or value is not None:
            setattr(x, field, value)
    await db.commit()
    return x


@router.delete("/client-log/{log_id}", status_code=204)
async def delete_log(log_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.delete(await _own(db, ClientLog, log_id, user))
    await db.commit()


# Invoices / expected payments
@router.get("/invoices", response_model=list[InvoiceOut])
async def list_invoices(unpaid: bool = Query(False), user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    today = await local_today(db, user)
    q = select(Invoice).where(Invoice.user_id == user.id)
    if unpaid:
        q = q.where(Invoice.paid_on.is_(None))
    return [invoice_out(i, today) for i in (await db.scalars(q.order_by(Invoice.due, Invoice.id))).all()]


@router.post("/clients/{client_id}/invoices", response_model=InvoiceOut, status_code=201)
async def create_invoice(client_id: int, body: InvoiceIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    c = await _client(db, client_id, user)
    await own_client(db, user, client_id, body.project_id)
    prefs = await prefs_of(db, user.id)
    issued = body.issued or await local_today(db, user)
    due = body.due or issued + timedelta(days=int((prefs.get("invoice") or {}).get("dueDays") or 14))
    number = body.number or await next_number(db, user, str((prefs.get("invoice") or {}).get("prefix") or ""), issued)
    items = [x.model_dump() for x in body.items]
    amount = body.amount if body.amount is not None else sum(Decimal(str(x["amount"])) for x in items)
    i = Invoice(
        user_id=user.id, client_id=client_id, project_id=body.project_id, number=number, title=body.title.strip(),
        amount=amount, currency=body.currency or c.currency, issued=issued, due=due, items=json.dumps(items, ensure_ascii=False), note=body.note,
    )
    db.add(i)
    await db.commit()
    return invoice_out(i, await local_today(db, user))


@router.patch("/invoices/{invoice_id}", response_model=InvoiceOut)
async def update_invoice(invoice_id: int, body: InvoicePatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    i = await _own(db, Invoice, invoice_id, user)
    for field in body.model_fields_set:
        value = getattr(body, field)
        if value is not None:
            setattr(i, field, value)
    await db.commit()
    return invoice_out(i, await local_today(db, user))


@router.delete("/invoices/{invoice_id}", status_code=204)
async def delete_invoice(invoice_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    i = await _own(db, Invoice, invoice_id, user)
    # Tracked time of this invoice becomes billable again
    for t in (await db.scalars(select(TimeEntry).where(TimeEntry.invoice_id == i.id))).all():
        t.invoice_id = None
    await db.delete(i)
    await db.commit()


@router.post("/invoices/{invoice_id}/pay", response_model=InvoiceOut)
async def pay_invoice(invoice_id: int, body: PayInvoiceIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Paid: records the income (category Projects, linked to the client) once."""
    i = await _own(db, Invoice, invoice_id, user)
    if i.paid_on is None:
        i.paid_on = body.paid_on or await local_today(db, user)
        entry = Income(user_id=user.id, category="projects", note=f"{i.number} {i.title}".strip()[:200], spent_on=i.paid_on, client_id=i.client_id, project_id=i.project_id)
        currency = i.currency if i.currency in ("EUR", "UAH", "USD") else "EUR"
        _convert(entry, i.amount, currency)
        db.add(entry)
        await db.flush()
        i.income_id = entry.id
        await db.commit()
    return invoice_out(i, await local_today(db, user))


@router.post("/invoices/{invoice_id}/unpay", response_model=InvoiceOut)
async def unpay_invoice(invoice_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Marked paid by mistake: removes the income it created."""
    i = await _own(db, Invoice, invoice_id, user)
    if i.income_id:
        income = await db.get(Income, i.income_id)
        if income:
            await db.delete(income)
    i.paid_on, i.income_id = None, None
    await db.commit()
    return invoice_out(i, await local_today(db, user))
