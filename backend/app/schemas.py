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
    client_id: int | None = None
    project_id: int | None = None


class CardPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    description: str | None = Field(None, max_length=10000)
    assignee_id: int | None = None
    column_id: int | None = None
    position: int | None = Field(None, ge=0)
    due_date: date | None = None
    is_private: bool | None = None
    client_id: int | None = None
    project_id: int | None = None


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
    client_id: int | None = None
    project_id: int | None = None


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
    member_ids: list[int] = Field(default_factory=list, max_length=50)


class BoardPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=120)
    position: int | None = Field(None, ge=0)


class MembersIn(BaseModel):
    user_ids: list[int] = Field(default_factory=list, max_length=50)


class BoardOut(Orm):
    id: int
    title: str
    created_by: int | None
    member_ids: list[int]

    @computed_field
    @property
    def is_private(self) -> bool:
        """Shared with nobody."""
        return not self.member_ids


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
    updated_at: datetime | None = None


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
    client_id: int | None = None
    project_id: int | None = None


class ExpensePatch(BaseModel):
    amount: Decimal | None = Field(None, gt=0, le=Decimal("100000000"), decimal_places=2)
    currency: Currency | None = None
    category: str | None = Field(None, min_length=1, max_length=20)
    note: str | None = Field(None, max_length=200)
    spent_on: date | None = None
    client_id: int | None = None
    project_id: int | None = None


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
    updated_at: datetime | None = None
    client_id: int | None = None
    project_id: int | None = None


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
    remind: int | None = Field(None, ge=0, le=10080)  # minutes before, up to a week
    client_id: int | None = None

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
    remind: int | None = Field(None, ge=0, le=10080)
    client_id: int | None = None

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
    remind: int | None
    updated_at: datetime | None = None
    client_id: int | None = None


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


# Calendar access
class CalendarAccessOut(BaseModel):
    shared_with: list[int]  # who can see my calendar
    shared_to_me: list[UserOut]  # whose calendars I can see
    enabled: bool = True  # sharing switched on (CALENDAR_SHARING)


class SettingsIn(BaseModel):
    data: dict = Field(default_factory=dict)


# Web Push
class PushKeys(BaseModel):
    p256dh: str = Field(min_length=1, max_length=200)
    auth: str = Field(min_length=1, max_length=100)


class SubscriptionIn(BaseModel):
    endpoint: str = Field(min_length=10, max_length=2000, pattern=r"^https://")
    keys: PushKeys


class UnsubscribeIn(BaseModel):
    endpoint: str = Field(max_length=2000)


class PushKeyOut(BaseModel):
    key: str  # VAPID public key (applicationServerKey)
    enabled: bool


class SnoozeIn(BaseModel):
    alarm_id: int
    time: str = Field(pattern=TIME_PATTERN)
    label: str = Field("", max_length=120)
    minutes: int = Field(10, ge=1, le=60)
    tag: str | None = Field(None, pattern=r"^[a-z0-9-]{1,60}$")  # notification tag of the app's own snooze


class SnoozeCancelIn(BaseModel):
    tag: str = Field(pattern=r"^[a-z0-9-]{1,60}$")


# "Today" screen (GET /today) and the morning summary
class TodayAlarm(BaseModel):
    id: int
    time: str
    label: str
    at: datetime  # next ring, user's time zone


class TodayEvent(BaseModel):
    id: int
    title: str
    start: str
    end: str
    color: str
    repeat: str
    note: str


class TodayCard(BaseModel):
    id: int
    title: str
    due_date: date | None
    assignee_id: int | None
    board_id: int
    board_title: str
    column_title: str
    done_column_id: int  # last column of the board = done


class TodayTasks(BaseModel):
    overdue: list[TodayCard] = []
    today: list[TodayCard] = []
    assigned: list[TodayCard] = []  # mine, no deadline due yet


class TodayBill(BaseModel):
    id: int
    title: str
    category: str
    amount: float | None
    currency: str
    day: int
    overdue: bool


class TodayMoney(BaseModel):
    month: str  # YYYY-MM
    spent_today: float  # EUR
    spent_month: float  # EUR
    bills: list[TodayBill] = []


class TodayClass(BaseModel):
    lesson_id: int
    subject_id: int
    subject: str
    color: str
    start: str
    end: str
    kind: str
    room: str


class TodayWork(BaseModel):
    id: int
    title: str
    kind: str
    subject: str | None
    color: str | None
    due: date
    due_time: str | None
    status: str


class TodayOut(BaseModel):
    date: date
    now: datetime
    tz: str
    next_alarm: TodayAlarm | None
    events: list[TodayEvent]
    tasks: TodayTasks
    money: TodayMoney
    classes: list[TodayClass] = []
    study: list[TodayWork] = []  # not done, due within a week or overdue
    followups: list["TodayFollowup"] = []  # "contact again" due by this day
    waiting: list["TodayInvoice"] = []  # unpaid invoices (overdue first)


class TodayFollowup(BaseModel):
    id: int
    client_id: int
    client: str
    text: str
    followup: date


class TodayInvoice(BaseModel):
    id: int
    client_id: int
    client: str
    title: str
    number: str
    amount: float
    currency: str
    due: date
    overdue: bool


# Study: semester, subjects with weekly classes, assignments / exams
StudyKind = Literal["assignment", "project", "exam", "credit"]
LessonKind = Literal["lecture", "seminar", "lab"]
Color = Field("#5B4BFF", pattern=r"^#[0-9A-Fa-f]{6}$")


class BreakRange(BaseModel):
    start: date = Field(alias="from")
    end: date = Field(alias="to")
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class SemesterIn(BaseModel):
    title: str = Title
    start: date
    end: date
    breaks: list[BreakRange] = Field(default_factory=list, max_length=60)
    remind: int | None = Field(None, ge=0, le=240)  # minutes before a class


class SemesterOut(BaseModel):
    id: int
    title: str
    start: date
    end: date
    breaks: list[BreakRange]
    remind: int | None


class StudyLink(BaseModel):
    title: str = Field("", max_length=60)
    url: str = Field(max_length=500, pattern=r"^https?://")


class SubjectIn(BaseModel):
    name: str = Title
    teacher: str = Field("", max_length=120)
    room: str = Field("", max_length=60)
    color: str = Color
    links: list[StudyLink] = Field(default_factory=list, max_length=10)
    note: str = Field("", max_length=5000)


class SubjectPatch(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    teacher: str | None = Field(None, max_length=120)
    room: str | None = Field(None, max_length=60)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    links: list[StudyLink] | None = Field(None, max_length=10)
    note: str | None = Field(None, max_length=5000)


class LessonIn(BaseModel):
    subject_id: int
    weekday: int = Field(ge=0, le=6)
    start: str = Field(pattern=TIME_PATTERN)
    end: str = Field(pattern=TIME_PATTERN)
    kind: LessonKind = "lecture"
    room: str = Field("", max_length=60)


class LessonOut(LessonIn):
    id: int


class LessonsIn(BaseModel):
    lessons: list[LessonIn] = Field(max_length=200)


class SubjectOut(BaseModel):
    id: int
    name: str
    teacher: str
    room: str
    color: str
    links: list[StudyLink]
    note: str
    lessons: list[LessonOut]


class WorkIn(BaseModel):
    subject_id: int | None = None
    kind: StudyKind = "assignment"
    title: str = Field(min_length=1, max_length=200)
    due: date
    due_time: str | None = Field(None, pattern=TIME_PATTERN)
    status: Literal["todo", "doing", "done"] = "todo"
    grade: str = Field("", max_length=20)
    note: str = Field("", max_length=5000)


class WorkPatch(BaseModel):
    subject_id: int | None = None
    kind: StudyKind | None = None
    title: str | None = Field(None, min_length=1, max_length=200)
    due: date | None = None
    due_time: str | None = Field(None, pattern=TIME_PATTERN)
    status: Literal["todo", "doing", "done"] | None = None
    grade: str | None = Field(None, max_length=20)
    note: str | None = Field(None, max_length=5000)


class WorkOut(Orm):
    id: int
    subject_id: int | None
    kind: str
    title: str
    due: date
    due_time: str | None
    status: str
    grade: str
    note: str
    updated_at: datetime | None = None


class StudyOut(BaseModel):
    semester: SemesterOut | None
    subjects: list[SubjectOut]
    works: list[WorkOut]


# ===== CRM =====
ClientStatus = Literal["lead", "active", "paused", "former"]
Money = Field(None, ge=0, le=Decimal("100000000"), decimal_places=2)


class ClientIn(BaseModel):
    name: str = Title
    company: str = Field("", max_length=120)
    email: str = Field("", max_length=200)
    phone: str = Field("", max_length=60)
    telegram: str = Field("", max_length=60)
    website: str = Field("", max_length=200)
    lang: str = Field("", max_length=5)
    currency: str = Field("EUR", pattern=r"^[A-Z]{3}$")
    rate: Decimal | None = Money
    tags: list[str] = Field(default_factory=list, max_length=20)
    note: str = Field("", max_length=10000)
    status: ClientStatus = "active"


class ClientPatch(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    company: str | None = Field(None, max_length=120)
    email: str | None = Field(None, max_length=200)
    phone: str | None = Field(None, max_length=60)
    telegram: str | None = Field(None, max_length=60)
    website: str | None = Field(None, max_length=200)
    lang: str | None = Field(None, max_length=5)
    currency: str | None = Field(None, pattern=r"^[A-Z]{3}$")
    rate: Decimal | None = Money
    tags: list[str] | None = Field(None, max_length=20)
    note: str | None = Field(None, max_length=10000)
    status: ClientStatus | None = None


class ClientOut(Orm):
    id: int
    name: str
    company: str
    email: str
    phone: str
    telegram: str
    website: str
    lang: str
    currency: str
    rate: float | None
    tags: list[str] | str
    note: str
    status: str


class ClientListItem(ClientOut):
    open_invoices: int = 0
    late_invoices: int = 0


class ProjectIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    status: Literal["active", "paused", "done"] = "active"
    budget: Decimal | None = Money
    rate: Decimal | None = Money
    start: date | None = None
    end: date | None = None


class ProjectPatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=160)
    status: Literal["active", "paused", "done"] | None = None
    budget: Decimal | None = Money
    rate: Decimal | None = Money
    start: date | None = None
    end: date | None = None


class ProjectOut(Orm):
    id: int
    client_id: int
    title: str
    status: str
    budget: float | None
    rate: float | None
    start: date | None
    end: date | None


class ClientLogIn(BaseModel):
    kind: Literal["call", "email", "meeting", "message"] = "message"
    day: date
    text: str = Field("", max_length=10000)
    followup: date | None = None


class ClientLogPatch(BaseModel):
    text: str | None = Field(None, max_length=10000)
    followup: date | None = None
    followup_done: bool | None = None


class ClientLogOut(Orm):
    id: int
    client_id: int
    kind: str
    day: date
    text: str
    followup: date | None
    followup_done: bool


class InvoiceItem(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    hours: float | None = Field(None, ge=0, le=10000)
    rate: float | None = Field(None, ge=0)
    amount: float = Field(ge=0)


class InvoiceIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    project_id: int | None = None
    number: str = Field("", max_length=40)
    amount: Decimal | None = Money  # None = sum of items
    currency: str | None = Field(None, pattern=r"^[A-Z]{3}$")
    issued: date | None = None
    due: date | None = None  # None = issued + due days from the invoice settings
    items: list[InvoiceItem] = Field(default_factory=list, max_length=100)
    note: str = Field("", max_length=2000)


class InvoicePatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    number: str | None = Field(None, max_length=40)
    amount: Decimal | None = Money
    due: date | None = None
    note: str | None = Field(None, max_length=2000)


class PayInvoiceIn(BaseModel):
    paid_on: date | None = None


class InvoiceOut(Orm):
    id: int
    client_id: int
    project_id: int | None
    number: str
    title: str
    amount: float
    currency: str
    issued: date
    due: date
    paid_on: date | None
    income_id: int | None
    items: list[InvoiceItem] | str
    note: str
    status: str = "pending"  # pending | overdue | paid


class OpenCard(BaseModel):
    id: int
    title: str
    due_date: date | None
    board_id: int
    board_title: str
    column_title: str


class MeetingOut(BaseModel):
    id: int
    title: str
    date: date
    start: str
    end: str


class ClientDetail(BaseModel):
    client: ClientOut
    projects: list[ProjectOut]
    log: list[ClientLogOut]
    invoices: list[InvoiceOut]
    cards: list[OpenCard]
    meetings: list[MeetingOut]
    earned_total: float  # EUR
    earned_month: float
    minutes_total: int
    minutes_month: int


# ===== Time tracking =====
class TimeStartIn(BaseModel):
    client_id: int | None = None
    project_id: int | None = None
    card_id: int | None = None
    note: str = Field("", max_length=300)
    start: datetime | None = None  # offline start: the moment it was pressed


class TimeStopIn(BaseModel):
    end: datetime | None = None


class TimeIn(BaseModel):
    client_id: int | None = None
    project_id: int | None = None
    card_id: int | None = None
    note: str = Field("", max_length=300)
    start: datetime
    end: datetime


class TimePatch(BaseModel):
    client_id: int | None = None
    project_id: int | None = None
    card_id: int | None = None
    note: str | None = Field(None, max_length=300)
    start: datetime | None = None
    end: datetime | None = None


class TimeOut(Orm):
    id: int
    client_id: int | None
    project_id: int | None
    card_id: int | None
    note: str
    start: datetime
    end: datetime | None
    invoice_id: int | None
    updated_at: datetime | None = None

    # Always with a time zone (SQLite returns naive UTC values)
    @field_validator("start", "end", "updated_at")
    @classmethod
    def _utc(cls, v: datetime | None) -> datetime | None:
        return v.replace(tzinfo=dt.timezone.utc) if v is not None and v.tzinfo is None else v


class ReportRow(BaseModel):
    client_id: int | None
    project_id: int | None
    card_id: int | None
    title: str  # card title or note
    minutes: int
    rate: float | None
    amount: float | None
    currency: str


class TimeReport(BaseModel):
    rows: list[ReportRow]
    minutes: int
    amounts: dict[str, float]  # per currency
    unbilled_minutes: int


class TimeInvoiceIn(BaseModel):
    client_id: int
    project_id: int | None = None
    start: date = Field(alias="from")
    end: date = Field(alias="to")
    title: str = Field("", max_length=200)
    model_config = ConfigDict(populate_by_name=True)


# Forward references (TodayOut lists types defined after it)
TodayOut.model_rebuild()
