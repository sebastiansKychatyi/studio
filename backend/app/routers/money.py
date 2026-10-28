import calendar
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import get_args

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_db
from ..models import CustomCategory, Expense, Income, MoneyEntry, Recurring, User
from ..schemas import (
    CategoryIn,
    CategoryOut,
    CategoryPatch,
    ExpenseCategory,
    ExpenseIn,
    ExpensePatch,
    IncomeCategory,
    IncomeIn,
    IncomePatch,
    MoneyOut,
    MonthTotal,
    PayIn,
    RecurringIn,
    RecurringOut,
    RecurringPatch,
)
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


def money_routes(
    path: str, model: type[MoneyEntry], body_in: type[BaseModel], body_patch: type[BaseModel], categories: tuple[str, ...]
) -> APIRouter:
    """Same CRUD, monthly summary and monthly templates for each kind of entry."""
    r = APIRouter(prefix=f"/{path}", tags=[path])

    # Category: built-in key or "c<id>" of the user's own category of this kind
    async def check_category(db: AsyncSession, user: User, category: str | None) -> None:
        if category is None or category in categories:
            return
        custom = await db.get(CustomCategory, int(category[1:])) if category[:1] == "c" and category[1:].isdigit() else None
        if custom is None or custom.user_id != user.id or custom.kind != path:
            raise HTTPException(422, "Unknown category")

    async def own_category(db: AsyncSession, cat_id: int, user: User) -> CustomCategory:
        cat = await db.get(CustomCategory, cat_id)
        if cat is None or cat.user_id != user.id or cat.kind != path:
            raise HTTPException(404, "Category not found")
        return cat

    @r.get("/categories", response_model=list[CategoryOut])
    async def list_categories(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        rows = await db.scalars(
            select(CustomCategory).where(CustomCategory.user_id == user.id, CustomCategory.kind == path).order_by(CustomCategory.id)
        )
        return rows.all()

    @r.post("/categories", response_model=CategoryOut, status_code=201)
    async def create_category(body: CategoryIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        cat = CustomCategory(user_id=user.id, kind=path, name=body.name.strip(), icon=body.icon, color=body.color)
        db.add(cat)
        await db.commit()
        return cat

    @r.patch("/categories/{cat_id}", response_model=CategoryOut)
    async def update_category(cat_id: int, body: CategoryPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        cat = await own_category(db, cat_id, user)
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(cat, field, value.strip() if field == "name" else value)
        await db.commit()
        return cat

    @r.delete("/categories/{cat_id}", status_code=204)
    async def delete_category(cat_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        cat = await own_category(db, cat_id, user)
        # Entries and templates of this category fall back to "other"
        key = f"c{cat.id}"
        await db.execute(update(model).where(model.user_id == user.id, model.category == key).values(category="other"))
        await db.execute(
            update(Recurring).where(Recurring.user_id == user.id, Recurring.kind == path, Recurring.category == key).values(category="other")
        )
        await db.delete(cat)
        await db.commit()

    # Monthly templates: rent, subscriptions, salary…

    async def own_template(db: AsyncSession, rec_id: int, user: User) -> Recurring:
        rec = await db.get(Recurring, rec_id)
        if rec is None or rec.user_id != user.id or rec.kind != path:
            raise HTTPException(404, "Template not found")
        return rec

    async def template_out(db: AsyncSession, rec: Recurring, month: str | None) -> RecurringOut:
        out = RecurringOut.model_validate(rec)
        last = await db.scalar(
            select(model).where(model.recurring_id == rec.id).order_by(model.spent_on.desc(), model.id.desc()).limit(1)
        )
        if last is not None:
            out.last_amount, out.last_currency = float(last.original_amount), last.currency
        if month:
            start = _month_start(month)
            entry = await db.scalar(
                select(model).where(model.recurring_id == rec.id, model.spent_on >= start, model.spent_on < _shift(start, 1)).limit(1)
            )
            out.entry = MoneyOut.model_validate(entry) if entry else None
        return out

    @r.get("/recurring", response_model=list[RecurringOut])
    async def list_templates(month: str = MONTH, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        rows = await db.scalars(
            select(Recurring).where(Recurring.user_id == user.id, Recurring.kind == path).order_by(Recurring.day, Recurring.id)
        )
        return [await template_out(db, rec, month) for rec in rows.all()]

    @r.post("/recurring", response_model=RecurringOut, status_code=201)
    async def create_template(body: RecurringIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        await check_category(db, user, body.category)
        rec = Recurring(user_id=user.id, kind=path, **body.model_dump())
        rec.title = rec.title.strip()
        db.add(rec)
        await db.commit()
        return RecurringOut.model_validate(rec)

    @r.patch("/recurring/{rec_id}", response_model=RecurringOut)
    async def update_template(rec_id: int, body: RecurringPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        rec = await own_template(db, rec_id, user)
        await check_category(db, user, body.category)
        for field in body.model_fields_set:
            value = getattr(body, field)
            # amount may be cleared (= variable); other fields only set
            if value is not None or field == "amount":
                setattr(rec, field, value.strip() if field == "title" else value)
        await db.commit()
        return await template_out(db, rec, None)

    @r.delete("/recurring/{rec_id}", status_code=204)
    async def delete_template(rec_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        # Past entries stay, only the link is cleared
        await db.delete(await own_template(db, rec_id, user))
        await db.commit()

    @r.post("/recurring/{rec_id}/pay", response_model=MoneyOut, status_code=201)
    async def pay_template(rec_id: int, body: PayIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
        """Mark as paid / received for a month: creates the entry from the template."""
        rec = await own_template(db, rec_id, user)
        start = _month_start(body.month)
        done = await db.scalar(
            select(model.id).where(model.recurring_id == rec.id, model.spent_on >= start, model.spent_on < _shift(start, 1))
        )
        if done:
            raise HTTPException(409, "Already marked for this month")
        amount = body.amount or (rec.amount if rec.amount is not None else None)
        if amount is None:
            raise HTTPException(422, "Amount required (template has a variable amount)")
        last_day = calendar.monthrange(start.year, start.month)[1]
        spent_on = body.spent_on or start.replace(day=min(rec.day, last_day))
        if not (start <= spent_on < _shift(start, 1)):
            raise HTTPException(422, "Date outside the month")
        entry = model(user_id=user.id, category=rec.category, note=rec.title, spent_on=spent_on, recurring_id=rec.id)
        _convert(entry, Decimal(amount), body.currency or rec.currency)
        db.add(entry)
        await db.commit()
        return entry

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
        await check_category(db, user, body.category)
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
        await check_category(db, user, body.category)
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


router.include_router(money_routes("expenses", Expense, ExpenseIn, ExpensePatch, get_args(ExpenseCategory)))
router.include_router(money_routes("income", Income, IncomeIn, IncomePatch, get_args(IncomeCategory)))
