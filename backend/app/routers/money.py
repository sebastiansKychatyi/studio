from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_db
from ..models import Expense, Income, MoneyEntry, User
from ..schemas import ExpenseIn, ExpensePatch, IncomeIn, IncomePatch, MoneyOut, MonthTotal
from ..security import current_user

# Expenses and income are personal, like alarms. Stored in EUR; UAH/USD converted with config rates.
router = APIRouter()


def _rates() -> dict[str, Decimal]:
    return {"EUR": Decimal(1), "UAH": Decimal(str(settings.rate_uah)), "USD": Decimal(str(settings.rate_usd))}


def _convert(entry: MoneyEntry, amount: Decimal, currency: str) -> None:
    rate = _rates()[currency]
    eur = (amount / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if eur <= 0 or eur > 1_000_000:
        raise HTTPException(422, "Amount out of range")
    entry.amount, entry.original_amount, entry.currency, entry.rate = eur, amount, currency, rate


MONTH = Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="YYYY-MM")


def _month_start(month: str) -> date:
    year, mon = map(int, month.split("-"))
    return date(year, mon, 1)


def _shift(d: date, months: int) -> date:
    total = d.year * 12 + d.month - 1 + months
    return date(total // 12, total % 12 + 1, 1)


@router.get("/rates", tags=["money"], dependencies=[Depends(current_user)])
async def rates() -> dict[str, float]:
    """1 EUR in each currency (from config)."""
    return {k: float(v) for k, v in _rates().items()}


def money_routes(path: str, model: type[MoneyEntry], body_in: type[BaseModel], body_patch: type[BaseModel]) -> APIRouter:
    """Same CRUD + monthly summary for each kind of entry."""
    r = APIRouter(prefix=f"/{path}", tags=[path])

    async def own(db: AsyncSession, entry_id: int, user: User) -> MoneyEntry:
        entry = await db.get(model, entry_id)
        if entry is None or entry.user_id != user.id:
            raise HTTPException(404, "Entry not found")
        return entry

    @r.get("", response_model=list[MoneyOut])
    async def list_entries(month: str = MONTH, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        start = _month_start(month)
        rows = await db.scalars(
            select(model)
            .where(model.user_id == user.id, model.spent_on >= start, model.spent_on < _shift(start, 1))
            .order_by(model.spent_on.desc(), model.id.desc())
        )
        return rows.all()

    @r.get("/summary", response_model=list[MonthTotal])
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
            select(model.spent_on, model.amount).where(
                model.user_id == user.id, model.spent_on >= start, model.spent_on < end
            )
        )
        for spent_on, amount in rows:
            totals[f"{spent_on:%Y-%m}"] += float(amount)
        return [MonthTotal(month=m, total=round(v, 2)) for m, v in totals.items()]

    @r.post("", response_model=MoneyOut, status_code=201)
    async def create_entry(body: body_in, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):  # type: ignore[valid-type]
        entry = model(user_id=user.id, category=body.category, note=body.note.strip(), spent_on=body.spent_on)
        _convert(entry, body.amount, body.currency)
        db.add(entry)
        await db.commit()
        return entry

    @r.patch("/{entry_id}", response_model=MoneyOut)
    async def update_entry(
        entry_id: int, body: body_patch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)  # type: ignore[valid-type]
    ):
        entry = await own(db, entry_id, user)
        if body.category is not None:
            entry.category = body.category
        if body.note is not None:
            entry.note = body.note.strip()
        if body.spent_on is not None:
            entry.spent_on = body.spent_on
        # New amount or currency → convert again with the current rate
        if body.amount is not None or body.currency is not None:
            _convert(entry, body.amount or entry.original_amount, body.currency or entry.currency)
        await db.commit()
        return entry

    @r.delete("/{entry_id}", status_code=204)
    async def delete_entry(entry_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        await db.delete(await own(db, entry_id, user))
        await db.commit()

    return r


router.include_router(money_routes("expenses", Expense, ExpenseIn, ExpensePatch))
router.include_router(money_routes("income", Income, IncomeIn, IncomePatch))
