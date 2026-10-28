import datetime as dt
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

Title = Field(min_length=1, max_length=120)


class Orm(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Auth / users
class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=200)


class UserOut(Orm):
    id: int
    username: str
    name: str


class MeOut(BaseModel):
    user: UserOut | None


# Kanban
class CardIn(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str = Field("", max_length=10000)
    assignee_id: int | None = None
    due_date: date | None = None
    is_private: bool = False


class CardPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = Field(None, max_length=10000)
    assignee_id: int | None = None
    column_id: int | None = None
    position: int | None = Field(None, ge=0)
    due_date: date | None = None
    is_private: bool | None = None


class CardOut(Orm):
    id: int
    column_id: int
    title: str
    description: str
    assignee_id: int | None
    created_by: int | None
    position: int
    due_date: date | None
    is_private: bool
    updated_at: datetime


class MentionOut(CardOut):
    board_id: int
    board_title: str
    column_title: str


class ColumnIn(BaseModel):
    title: str = Title


class ColumnPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=120)
    position: int | None = Field(None, ge=0)


class ColumnOut(Orm):
    id: int
    title: str
    position: int
    cards: list[CardOut] = []


class BoardIn(BaseModel):
    title: str = Title
    columns: list[str] = Field(default_factory=list, max_length=12)
    is_private: bool = False


class BoardPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=120)
    is_private: bool | None = None
    position: int | None = Field(None, ge=0)


class BoardOut(Orm):
    id: int
    title: str
    is_private: bool
    created_by: int | None


class ColumnRef(Orm):
    id: int
    title: str


class BoardListItem(BoardOut):
    columns: list[ColumnRef]


class BoardFull(BoardOut):
    columns: list[ColumnOut]


# Alarms
TIME_PATTERN = r"^([01]\d|2[0-3]):[0-5]\d$"


def _check_days(v: list[int] | None) -> list[int] | None:
    if v is not None and any(d < 0 or d > 6 for d in v):
        raise ValueError("days must be 0..6")
    return sorted(set(v)) if v is not None else None


class AlarmIn(BaseModel):
    time: str = Field(pattern=TIME_PATTERN)
    label: str = Field("", max_length=120)
    days: list[int] = Field(default_factory=list, max_length=7)
    enabled: bool = True

    _days = field_validator("days")(_check_days)


class AlarmPatch(BaseModel):
    time: str | None = Field(None, pattern=TIME_PATTERN)
    label: str | None = Field(None, max_length=120)
    days: list[int] | None = Field(None, max_length=7)
    enabled: bool | None = None

    _days = field_validator("days")(_check_days)


class AlarmOut(BaseModel):
    id: int
    time: str
    label: str
    days: list[int]
    enabled: bool


# Expenses / income: entered in EUR/UAH/USD, stored in EUR
ExpenseCategory = Literal["food", "transport", "home", "software", "tech", "fun", "health", "other"]
IncomeCategory = Literal["projects", "salary", "support", "sale", "gift", "refund", "other"]
Currency = Literal["EUR", "UAH", "USD"]
Amount = Field(gt=0, le=Decimal("100000000"), decimal_places=2)


# Built-in key or "c<id>" of a custom category; checked in the router
CategoryKey = Field("other", min_length=1, max_length=20)


class ExpenseIn(BaseModel):
    amount: Decimal = Amount
    currency: Currency = "EUR"
    category: str = CategoryKey
    note: str = Field("", max_length=200)
    spent_on: date


class ExpensePatch(BaseModel):
    amount: Decimal | None = Field(None, gt=0, le=Decimal("100000000"), decimal_places=2)
    currency: Currency | None = None
    category: str | None = Field(None, min_length=1, max_length=20)
    note: str | None = Field(None, max_length=200)
    spent_on: date | None = None


class IncomeIn(ExpenseIn):
    pass


class IncomePatch(ExpensePatch):
    pass


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    icon: str = Field("tag", pattern=r"^[a-z]{1,20}$")
    color: str = Field("#9CA3AF", pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryPatch(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=40)
    icon: str | None = Field(None, pattern=r"^[a-z]{1,20}$")
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryOut(Orm):
    id: int
    name: str
    icon: str
    color: str

    @computed_field
    @property
    def key(self) -> str:
        return f"c{self.id}"


class MoneyOut(Orm):
    id: int
    amount: float  # EUR
    original_amount: float
    currency: str
    rate: float
    category: str
    note: str
    spent_on: date
    recurring_id: int | None = None


# Monthly templates (category is checked against the kind in the router)
class RecurringIn(BaseModel):
    title: str = Title
    category: str = Field("other", max_length=20)
    amount: Decimal | None = Field(None, gt=0, le=Decimal("100000000"), decimal_places=2)
    currency: Currency = "EUR"
    day: int = Field(1, ge=1, le=31)


class RecurringPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=120)
    category: str | None = Field(None, max_length=20)
    amount: Decimal | None = Field(None, gt=0, le=Decimal("100000000"), decimal_places=2)
    currency: Currency | None = None
    day: int | None = Field(None, ge=1, le=31)


class RecurringOut(Orm):
    id: int
    title: str
    category: str
    amount: float | None
    currency: str
    day: int
    entry: MoneyOut | None = None  # this month's payment, if done
    last_amount: float | None = None  # last paid amount (in last_currency), hint for variable amounts
    last_currency: str | None = None


class PayIn(BaseModel):
    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    amount: Decimal | None = Field(None, gt=0, le=Decimal("100000000"), decimal_places=2)
    currency: Currency | None = None
    spent_on: date | None = None


class MonthTotal(BaseModel):
    month: str  # YYYY-MM
    total: float


# Calendar
class EventIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    date: dt.date
    start: str = Field(pattern=TIME_PATTERN)
    end: str = Field(pattern=TIME_PATTERN)
    repeat: Literal["none", "weekly"] = "none"
    days: list[int] = Field(default_factory=list, max_length=7)
    until: dt.date | None = None
    color: str = Field("#5B4BFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    note: str = Field("", max_length=5000)

    _days = field_validator("days")(_check_days)


class EventPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    date: dt.date | None = None
    start: str | None = Field(None, pattern=TIME_PATTERN)
    end: str | None = Field(None, pattern=TIME_PATTERN)
    repeat: Literal["none", "weekly"] | None = None
    days: list[int] | None = Field(None, max_length=7)
    until: dt.date | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    note: str | None = Field(None, max_length=5000)

    _days = field_validator("days")(_check_days)


class EventOut(BaseModel):
    id: int
    title: str
    date: dt.date
    start: str
    end: str
    repeat: str
    days: list[int]
    until: dt.date | None
    skip: list[dt.date]
    color: str
    note: str


class SkipIn(BaseModel):
    date: date


class DueCard(BaseModel):
    id: int
    title: str
    due_date: date
    board_id: int
    board_title: str
    column_title: str
    done: bool  # in the last column
