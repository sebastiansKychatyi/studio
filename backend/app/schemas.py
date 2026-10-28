from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


class CardPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = Field(None, max_length=10000)
    assignee_id: int | None = None
    column_id: int | None = None
    position: int | None = Field(None, ge=0)


class CardOut(Orm):
    id: int
    column_id: int
    title: str
    description: str
    assignee_id: int | None
    created_by: int | None
    position: int
    updated_at: datetime


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


class BoardPatch(BaseModel):
    title: str = Title


class BoardOut(Orm):
    id: int
    title: str


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


# Expenses (EUR)
Category = Literal["food", "transport", "home", "software", "tech", "fun", "health", "other"]
Amount = Field(gt=0, le=Decimal("1000000"), decimal_places=2)


class ExpenseIn(BaseModel):
    amount: Decimal = Amount
    category: Category = "other"
    note: str = Field("", max_length=200)
    spent_on: date


class ExpensePatch(BaseModel):
    amount: Decimal | None = Field(None, gt=0, le=Decimal("1000000"), decimal_places=2)
    category: Category | None = None
    note: str | None = Field(None, max_length=200)
    spent_on: date | None = None


class ExpenseOut(Orm):
    id: int
    amount: float
    category: str
    note: str
    spent_on: date


class MonthTotal(BaseModel):
    month: str  # YYYY-MM
    total: float
