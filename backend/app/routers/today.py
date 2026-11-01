import calendar
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_db
from ..models import Alarm, Board, BoardColumn, CalEvent, Expense, Recurring, User
from ..notify import occurs, prefs_of, tz_of
from ..schemas import TodayAlarm, TodayBill, TodayCard, TodayEvent, TodayMoney, TodayOut, TodayTasks
from ..security import current_user
from .kanban import can_see_board, can_see_card

# "Today" screen: the whole day in one request, in the user's time zone (also used by the morning summary)
router = APIRouter(tags=["today"])


async def next_alarm(db: AsyncSession, user_id: int, now: datetime) -> TodayAlarm | None:
    alarms = (await db.scalars(select(Alarm).where(Alarm.user_id == user_id, Alarm.enabled))).all()
    best: TodayAlarm | None = None
    for a in alarms:
        h, m = map(int, a.time.split(":"))
        days = {int(d) for d in a.days.split(",") if d}
        for k in range(8):
            d = now.date() + timedelta(days=k)
            at = datetime(d.year, d.month, d.day, h, m, tzinfo=now.tzinfo)
            if at > now and (not days or (d.weekday() + 1) % 7 in days):
                if best is None or at < best.at:
                    best = TodayAlarm(id=a.id, time=a.time, label=a.label, at=at)
                break
    return best


async def build_today(db: AsyncSession, user: User, day: date | None = None) -> TodayOut:
    prefs = await prefs_of(db, user.id)
    tz = tz_of(prefs)
    now = datetime.now(tz)
    day = day or now.date()

    events = [
        TodayEvent(id=e.id, title=e.title, start=e.start, end=e.end, color=e.color, repeat=e.repeat, note=e.note)
        for e in (await db.scalars(select(CalEvent).where(CalEvent.user_id == user.id))).all()
        if occurs(e, day)
    ]
    events.sort(key=lambda e: (e.start, e.end))

    # Open cards (not in a board's last column) the user can see
    tasks = TodayTasks()
    boards = (await db.scalars(select(Board).options(selectinload(Board.columns).selectinload(BoardColumn.cards)))).all()
    for board in boards:
        if not can_see_board(board, user) or not board.columns:
            continue
        done = board.columns[-1]
        for column in board.columns[:-1]:
            for card in column.cards:
                if not can_see_card(card, user):
                    continue
                item = TodayCard(
                    id=card.id, title=card.title, due_date=card.due_date, assignee_id=card.assignee_id,
                    board_id=board.id, board_title=board.title, column_title=column.title, done_column_id=done.id,
                )
                mine = card.assignee_id == user.id or (card.assignee_id is None and card.created_by == user.id)
                if card.due_date and card.due_date < day and mine:
                    tasks.overdue.append(item)
                elif card.due_date == day and mine:
                    tasks.today.append(item)
                elif card.assignee_id == user.id and not card.due_date:
                    tasks.assigned.append(item)
    tasks.overdue.sort(key=lambda c: c.due_date)

    # Money in EUR: spent today / this month, monthly payments due by this day and not paid
    start = day.replace(day=1)
    end = start.replace(day=calendar.monthrange(day.year, day.month)[1])
    spent = lambda a, b: db.scalar(  # noqa: E731
        select(func.coalesce(func.sum(Expense.amount), 0)).where(Expense.user_id == user.id, Expense.spent_on >= a, Expense.spent_on <= b)
    )
    bills = []
    for tpl in (await db.scalars(select(Recurring).where(Recurring.user_id == user.id, Recurring.kind == "expenses"))).all():
        due = min(tpl.day, end.day)
        if due > day.day:
            continue
        paid = await db.scalar(select(func.count()).select_from(Expense).where(Expense.recurring_id == tpl.id, Expense.spent_on >= start, Expense.spent_on <= end))
        if not paid:
            bills.append(TodayBill(
                id=tpl.id, title=tpl.title, category=tpl.category, amount=float(tpl.amount) if tpl.amount is not None else None,
                currency=tpl.currency, day=due, overdue=due < day.day,
            ))
    money = TodayMoney(month=f"{start:%Y-%m}", spent_today=float(await spent(day, day)), spent_month=float(await spent(start, end)), bills=bills)

    return TodayOut(
        date=day, now=now, tz=str(tz), next_alarm=await next_alarm(db, user.id, now), events=events, tasks=tasks, money=money,
    )


@router.get("/today", response_model=TodayOut)
async def today(day: date | None = Query(None, alias="date"), user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await build_today(db, user, day)
