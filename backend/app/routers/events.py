from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_db
from ..models import Board, BoardColumn, CalendarShare, CalEvent, User
from ..schemas import CalendarAccessOut, DueCard, EventIn, EventOut, EventPatch, MembersIn, SkipIn, UserOut
from ..security import current_user
from .kanban import can_see_board, can_see_card

# Personal calendar: events belong to their owner; the owner can let chosen people see them (read-only).
# Repeats are expanded on the client (few events, any range).
router = APIRouter(tags=["calendar"])


def _out(e: CalEvent) -> EventOut:
    return EventOut(
        id=e.id,
        title=e.title,
        date=e.date,
        start=e.start,
        end=e.end,
        repeat=e.repeat,
        days=[int(d) for d in e.days.split(",") if d],
        until=e.until,
        skip=[date.fromisoformat(d) for d in e.skip.split(",") if d],
        color=e.color,
        note=e.note,
        remind=e.remind,
    )


def _check(e: CalEvent) -> None:
    if e.end <= e.start:
        raise HTTPException(422, "End must be after start")
    if e.until is not None and e.until < e.date:
        raise HTTPException(422, "Until must not be before the first day")
    if e.repeat == "weekly" and not e.days:
        # Default: the weekday of the first day (JS numbering, 0 = Sunday)
        e.days = str((e.date.weekday() + 1) % 7)


async def _own(db: AsyncSession, event_id: int, user: User) -> CalEvent:
    e = await db.get(CalEvent, event_id)
    if e is None or e.user_id != user.id:
        raise HTTPException(404, "Event not found")
    return e


@router.get("/events", response_model=list[EventOut])
async def list_events(
    owner: int | None = Query(None, alias="user", description="Another user's calendar (needs their permission)"),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    owner_id = owner or user.id
    if owner_id != user.id and await db.get(CalendarShare, (owner_id, user.id)) is None:
        raise HTTPException(404, "Calendar not shared with you")
    rows = await db.scalars(select(CalEvent).where(CalEvent.user_id == owner_id).order_by(CalEvent.date, CalEvent.start))
    return [_out(e) for e in rows.all()]


@router.get("/calendar/access", response_model=CalendarAccessOut)
async def calendar_access(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    mine = await db.scalars(select(CalendarShare.viewer_id).where(CalendarShare.owner_id == user.id))
    theirs = await db.scalars(
        select(User).join(CalendarShare, CalendarShare.owner_id == User.id).where(CalendarShare.viewer_id == user.id).order_by(User.name)
    )
    return CalendarAccessOut(shared_with=sorted(mine.all()), shared_to_me=[UserOut.model_validate(u) for u in theirs.all()])


@router.put("/calendar/access", response_model=CalendarAccessOut)
async def set_calendar_access(body: MembersIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Who may see my calendar (read-only)."""
    ids = sorted(set(body.user_ids) - {user.id})
    if ids and len((await db.scalars(select(User.id).where(User.id.in_(ids)))).all()) != len(ids):
        raise HTTPException(404, "User not found")
    await db.execute(delete(CalendarShare).where(CalendarShare.owner_id == user.id))
    db.add_all(CalendarShare(owner_id=user.id, viewer_id=uid) for uid in ids)
    await db.commit()
    return await calendar_access(user, db)


@router.post("/events", response_model=EventOut, status_code=201)
async def create_event(body: EventIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    data = body.model_dump()
    data["days"] = ",".join(map(str, data["days"])) if body.repeat == "weekly" else ""
    e = CalEvent(user_id=user.id, **data)
    e.title = e.title.strip()
    _check(e)
    db.add(e)
    await db.commit()
    return _out(e)


@router.patch("/events/{event_id}", response_model=EventOut)
async def update_event(event_id: int, body: EventPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    e = await _own(db, event_id, user)
    for field in body.model_fields_set:
        value = getattr(body, field)
        if field == "days":
            e.days = ",".join(map(str, value or []))
        elif field in ("until", "remind"):
            setattr(e, field, value)  # may be cleared
        elif value is not None:
            setattr(e, field, value.strip() if field == "title" else value)
    if e.repeat != "weekly":
        e.days, e.until, e.skip = "", None, ""
    _check(e)
    await db.commit()
    return _out(e)


@router.post("/events/{event_id}/skip", response_model=EventOut)
async def skip_day(event_id: int, body: SkipIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Cancel one occurrence of a repeating event (e.g. no class that day)."""
    e = await _own(db, event_id, user)
    days = {d for d in e.skip.split(",") if d}
    days.add(body.date.isoformat())
    e.skip = ",".join(sorted(days))
    await db.commit()
    return _out(e)


@router.delete("/events/{event_id}", status_code=204)
async def delete_event(event_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.delete(await _own(db, event_id, user))
    await db.commit()


@router.get("/due", response_model=list[DueCard])
async def due_cards(
    start: date = Query(alias="from"),
    end: date = Query(alias="to"),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    """Kanban cards with a deadline in [from, to] that the user can see."""
    boards = (await db.scalars(select(Board).options(selectinload(Board.columns).selectinload(BoardColumn.cards)))).all()
    out = []
    for board in boards:
        if not can_see_board(board, user):
            continue
        last = board.columns[-1].id if board.columns else None
        for column in board.columns:
            for card in column.cards:
                if card.due_date and start <= card.due_date <= end and can_see_card(card, user):
                    out.append(
                        DueCard(
                            id=card.id,
                            title=card.title,
                            due_date=card.due_date,
                            board_id=board.id,
                            board_title=board.title,
                            column_title=column.title,
                            done=column.id == last,
                        )
                    )
    return sorted(out, key=lambda c: (c.due_date, c.id))
