from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_db
from ..models import Expense, User
from ..schemas import ExpenseIn, ExpenseOut, ExpensePatch, MonthTotal
from ..security import current_user

# Expenses are personal, like alarms. Stored in EUR; UAH/USD converted with config rates.
router = APIRouter(tags=["expenses"])


def _rates() -> dict[str, Decimal]:
    return {"EUR": Decimal(1), "UAH": Decimal(str(settings.rate_uah)), "USD": Decimal(str(settings.rate_usd))}


def _convert(expense: Expense, amount: Decimal, currency: str) -> None:
    rate = _rates()[currency]
    eur = (amount / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if eur <= 0 or eur > 1_000_000:
        raise HTTPException(422, "Amount out of range")
    expense.amount, expense.original_amount, expense.currency, expense.rate = eur, amount, currency, rate


MONTH = Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="YYYY-MM")


def _month_start(month: str) -> date:
    year, mon = map(int, month.split("-"))
    return date(year, mon, 1)


def _shift(d: date, months: int) -> date:
    total = d.year * 12 + d.month - 1 + months
    return date(total // 12, total % 12 + 1, 1)


async def _own(db: AsyncSession, expense_id: int, user: User) -> Expense:
    expense = await db.get(Expense, expense_id)
    if expense is None or expense.user_id != user.id:
        raise HTTPException(404, "Expense not found")
    return expense


@router.get("/expenses", response_model=list[ExpenseOut])
async def list_expenses(month: str = MONTH, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    start = _month_start(month)
    rows = await db.scalars(
        select(Expense)
        .where(Expense.user_id == user.id, Expense.spent_on >= start, Expense.spent_on < _shift(start, 1))
        .order_by(Expense.spent_on.desc(), Expense.id.desc())
    )
    return rows.all()


@router.get("/expenses/rates", dependencies=[Depends(current_user)])
async def rates() -> dict[str, float]:
    """1 EUR in each currency (from config)."""
    return {k: float(v) for k, v in _rates().items()}


@router.get("/expenses/summary", response_model=list[MonthTotal])
async def summary(
    month: str = MONTH,
    months: int = Query(6, ge=1, le=24),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    """Totals for `months` months ending with `month`, oldest first."""
    end = _shift(_month_start(month), 1)
    start = _shift(end, -months)
    totals = {f"{_shift(start, i):%Y-%m}": 0.0 for i in range(months)}
    rows = await db.execute(
        select(Expense.spent_on, Expense.amount).where(
            Expense.user_id == user.id, Expense.spent_on >= start, Expense.spent_on < end
        )
    )
    for spent_on, amount in rows:
        totals[f"{spent_on:%Y-%m}"] += float(amount)
    return [MonthTotal(month=m, total=round(v, 2)) for m, v in totals.items()]


@router.post("/expenses", response_model=ExpenseOut, status_code=201)
async def create_expense(body: ExpenseIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    expense = Expense(user_id=user.id, category=body.category, note=body.note.strip(), spent_on=body.spent_on)
    _convert(expense, body.amount, body.currency)
    db.add(expense)
    await db.commit()
    return expense


@router.patch("/expenses/{expense_id}", response_model=ExpenseOut)
async def update_expense(
    expense_id: int, body: ExpensePatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)
):
    expense = await _own(db, expense_id, user)
    if body.category is not None:
        expense.category = body.category
    if body.note is not None:
        expense.note = body.note.strip()
    if body.spent_on is not None:
        expense.spent_on = body.spent_on
    # New amount or currency → convert again with the current rate
    if body.amount is not None or body.currency is not None:
        _convert(expense, body.amount or expense.original_amount, body.currency or expense.currency)
    await db.commit()
    return expense


@router.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(expense_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.delete(await _own(db, expense_id, user))
    await db.commit()
