import datetime as dt
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .sync import utcnow


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120), server_default="")
    # bcrypt hash; pgcrypto crypt(pw, gen_salt('bf')) is compatible
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Session(Base):
    __tablename__ = "sessions"

    # sha256 of the cookie token; raw token is never stored
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    position: Mapped[int] = mapped_column(Integer, server_default="0")
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    # Legacy flag (before per-person access); kept for the one-time migration only
    is_private: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    columns: Mapped[list["BoardColumn"]] = relationship(
        back_populates="board", order_by="BoardColumn.position", cascade="all, delete-orphan", passive_deletes=True
    )
    # People the creator shared the board with
    members: Mapped[list["BoardMember"]] = relationship(lazy="selectin", cascade="all, delete-orphan", passive_deletes=True)

    @property
    def member_ids(self) -> list[int]:
        return sorted(m.user_id for m in self.members)


class BoardMember(Base):
    __tablename__ = "board_members"

    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)


class BoardColumn(Base):
    __tablename__ = "board_columns"

    id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    position: Mapped[int] = mapped_column(Integer, server_default="0")

    board: Mapped[Board] = relationship(back_populates="columns")
    cards: Mapped[list["Card"]] = relationship(
        back_populates="column", order_by="Card.position", cascade="all, delete-orphan", passive_deletes=True
    )


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    column_id: Mapped[int] = mapped_column(ForeignKey("board_columns.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, server_default="")
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    position: Mapped[int] = mapped_column(Integer, server_default="0")
    due_date: Mapped[date | None] = mapped_column(Date)
    # Private cards are visible only to created_by
    is_private: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    # CRM link (the client list is personal: only its owner sees the name)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"))
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    column: Mapped[BoardColumn] = relationship(back_populates="cards")


class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    time: Mapped[str] = mapped_column(String(5))  # HH:MM
    label: Mapped[str] = mapped_column(String(120), server_default="")
    # JS weekdays "1,2,3" (0 = Sunday); empty = ring once
    days: Mapped[str] = mapped_column(String(20), server_default="")
    enabled: Mapped[bool] = mapped_column(Boolean, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Set in Python (no reload after commit); offline sync compares it (see sync.py)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), default=utcnow, onupdate=utcnow)


class MoneyEntry:
    """Shared columns for expenses and income. Amount always in EUR."""

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # always EUR
    # What was entered and the rate used (1 EUR = rate units of currency)
    original_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3), server_default="EUR")
    rate: Mapped[Decimal] = mapped_column(Numeric(12, 4), server_default="1")
    category: Mapped[str] = mapped_column(String(20), server_default="other")
    note: Mapped[str] = mapped_column(String(200), server_default="")
    spent_on: Mapped[date] = mapped_column(Date, index=True)  # entry date (also for income)
    # Set when created from a monthly template ("paid" / "received")
    recurring_id: Mapped[int | None] = mapped_column(ForeignKey("recurring.id", ondelete="SET NULL"), index=True)
    # Income from a client / project (CRM totals)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Set in Python (no reload after commit); offline sync compares it (see sync.py)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), default=utcnow, onupdate=utcnow)


class CalEvent(Base):
    """Personal calendar event; weekly events repeat on `days` until `until` (minus `skip` dates)."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    date: Mapped[dt.date] = mapped_column(Date)  # first day (or the only one)
    start: Mapped[str] = mapped_column(String(5))  # HH:MM
    end: Mapped[str] = mapped_column(String(5))  # HH:MM
    repeat: Mapped[str] = mapped_column(String(10), server_default="none")  # none | weekly
    # JS weekdays "1,3" (0 = Sunday) for weekly
    days: Mapped[str] = mapped_column(String(20), server_default="")
    until: Mapped[dt.date | None] = mapped_column(Date)
    # Cancelled occurrences "YYYY-MM-DD,…"
    skip: Mapped[str] = mapped_column(Text, server_default="")
    color: Mapped[str] = mapped_column(String(7), server_default="#5B4BFF")
    note: Mapped[str] = mapped_column(Text, server_default="")
    remind: Mapped[int | None] = mapped_column(Integer)  # minutes before start; None = no reminder
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"))  # meeting with a client
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Set in Python (no reload after commit); offline sync compares it (see sync.py)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), default=utcnow, onupdate=utcnow)


class CalendarShare(Base):
    """owner lets viewer see (read-only) their calendar."""

    __tablename__ = "calendar_shares"

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    viewer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)


class UserSettings(Base):
    """Per-account UI settings (theme, layouts, currency…) as JSON."""

    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    data: Mapped[str] = mapped_column(Text, server_default="{}")


class Recurring(Base):
    """Monthly template: rent, subscriptions, salary… amount None = varies every month."""

    __tablename__ = "recurring"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(10))  # expenses | income
    title: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(20), server_default="other")
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))  # in `currency`
    currency: Mapped[str] = mapped_column(String(3), server_default="EUR")
    day: Mapped[int] = mapped_column(Integer, server_default="1")  # day of month, clamped to month length
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CustomCategory(Base):
    """User's own category for expenses or income; entries refer to it as "c<id>"."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(10))  # expenses | income
    name: Mapped[str] = mapped_column(String(40))
    icon: Mapped[str] = mapped_column(String(20), server_default="tag")
    color: Mapped[str] = mapped_column(String(7), server_default="#9CA3AF")


class Expense(MoneyEntry, Base):
    __tablename__ = "expenses"


class Income(MoneyEntry, Base):
    __tablename__ = "incomes"


class PushSubscription(Base):
    """Web Push endpoint of one browser/device; a user can have several."""

    __tablename__ = "push_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    endpoint: Mapped[str] = mapped_column(Text, unique=True)
    p256dh: Mapped[str] = mapped_column(String(200))
    auth: Mapped[str] = mapped_column(String(100))
    user_agent: Mapped[str] = mapped_column(String(300), server_default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PushSent(Base):
    """Scheduled notifications already sent (one row per alarm/reminder occurrence), kept a few days."""

    __tablename__ = "push_sent"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PushLater(Base):
    """One-off notification at a given time (alarm snoozed from the notification)."""

    __tablename__ = "push_later"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    fire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    payload: Mapped[str] = mapped_column(Text)  # JSON for the service worker


class Semester(Base):
    """Study period; classes repeat weekly between start and end, except on break days."""

    __tablename__ = "semesters"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    start: Mapped[dt.date] = mapped_column(Date)
    end: Mapped[dt.date] = mapped_column(Date)
    # No classes: "YYYY-MM-DD" or "YYYY-MM-DD:YYYY-MM-DD" (holidays, exam period), comma separated
    breaks: Mapped[str] = mapped_column(Text, server_default="")
    remind: Mapped[int | None] = mapped_column(Integer)  # minutes before a class; None = no reminder
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semesters.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    teacher: Mapped[str] = mapped_column(String(120), server_default="")
    room: Mapped[str] = mapped_column(String(60), server_default="")
    color: Mapped[str] = mapped_column(String(7), server_default="#5B4BFF")
    links: Mapped[str] = mapped_column(Text, server_default="[]")  # JSON [{title, url}] (Moodle, Teams…)
    note: Mapped[str] = mapped_column(Text, server_default="")

    lessons: Mapped[list["Lesson"]] = relationship(
        lazy="selectin", order_by="Lesson.weekday, Lesson.start", cascade="all, delete-orphan", passive_deletes=True
    )


class Lesson(Base):
    """Weekly class of a subject: lecture, seminar or lab."""

    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    weekday: Mapped[int] = mapped_column(Integer)  # JS weekday, 0 = Sunday
    start: Mapped[str] = mapped_column(String(5))  # HH:MM
    end: Mapped[str] = mapped_column(String(5))
    kind: Mapped[str] = mapped_column(String(10), server_default="lecture")  # lecture | seminar | lab
    room: Mapped[str] = mapped_column(String(60), server_default="")  # empty = the subject's room


class StudyWork(Base):
    """Assignment, coursework, exam or credit test with a deadline."""

    __tablename__ = "study_works"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[int | None] = mapped_column(ForeignKey("subjects.id", ondelete="SET NULL"), index=True)
    kind: Mapped[str] = mapped_column(String(12), server_default="assignment")  # assignment | project | exam | credit
    title: Mapped[str] = mapped_column(String(200))
    due: Mapped[dt.date] = mapped_column(Date, index=True)
    due_time: Mapped[str | None] = mapped_column(String(5))  # HH:MM, optional
    status: Mapped[str] = mapped_column(String(8), server_default="todo")  # todo | doing | done
    grade: Mapped[str] = mapped_column(String(20), server_default="")
    note: Mapped[str] = mapped_column(Text, server_default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), default=utcnow, onupdate=utcnow)


# ===== CRM (personal) =====
class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    company: Mapped[str] = mapped_column(String(120), server_default="")
    email: Mapped[str] = mapped_column(String(200), server_default="", index=True)
    phone: Mapped[str] = mapped_column(String(60), server_default="")
    telegram: Mapped[str] = mapped_column(String(60), server_default="")
    website: Mapped[str] = mapped_column(String(200), server_default="")
    lang: Mapped[str] = mapped_column(String(5), server_default="")  # language of communication
    currency: Mapped[str] = mapped_column(String(3), server_default="EUR")
    rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # default hourly rate in `currency`
    tags: Mapped[str] = mapped_column(String(300), server_default="")  # comma separated
    note: Mapped[str] = mapped_column(Text, server_default="")
    status: Mapped[str] = mapped_column(String(8), server_default="active")  # lead | active | paused | former
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), default=utcnow, onupdate=utcnow)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(8), server_default="active")  # active | paused | done
    budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # fixed price in the client currency
    rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # hourly; None = rate of the client
    start: Mapped[dt.date | None] = mapped_column(Date)
    end: Mapped[dt.date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ClientLog(Base):
    """Contact history: call / email / meeting / message, optionally "contact again on"."""

    __tablename__ = "client_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(10), server_default="message")  # call | email | meeting | message
    day: Mapped[dt.date] = mapped_column(Date)
    text: Mapped[str] = mapped_column(Text, server_default="")
    followup: Mapped[dt.date | None] = mapped_column(Date, index=True)  # reminder on Today + push
    followup_done: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Invoice(Base):
    """Amount a client owes: entered by hand or made from tracked time; paying it creates an income entry."""

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
    number: Mapped[str] = mapped_column(String(40), server_default="")
    title: Mapped[str] = mapped_column(String(200))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))  # in `currency`
    currency: Mapped[str] = mapped_column(String(3), server_default="EUR")
    issued: Mapped[dt.date] = mapped_column(Date)
    due: Mapped[dt.date] = mapped_column(Date, index=True)
    paid_on: Mapped[dt.date | None] = mapped_column(Date)
    income_id: Mapped[int | None] = mapped_column(ForeignKey("incomes.id", ondelete="SET NULL"))
    items: Mapped[str] = mapped_column(Text, server_default="[]")  # JSON [{title, hours, rate, amount}] for the PDF
    note: Mapped[str] = mapped_column(Text, server_default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TimeEntry(Base):
    """Tracked time; end None = the running timer (one per user)."""

    __tablename__ = "time_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
    card_id: Mapped[int | None] = mapped_column(ForeignKey("cards.id", ondelete="SET NULL"))
    note: Mapped[str] = mapped_column(String(300), server_default="")
    start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    invoice_id: Mapped[int | None] = mapped_column(ForeignKey("invoices.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), default=utcnow, onupdate=utcnow)


# ===== e-Drivebook monitoring (see monitoring.py) =====
class MonitorProject(Base):
    """A monitored web application (e-Drivebook, …); its environments follow the shared monitoring contract."""

    __tablename__ = "monitor_projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str] = mapped_column(Text, server_default="", default="")
    enabled: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MonitorEnv(Base):
    """One environment of a project and its last known state. Token and secret never leave the server."""

    __tablename__ = "monitor_envs"
    __table_args__ = (UniqueConstraint("project_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)  # also in the webhook URL
    project_id: Mapped[int] = mapped_column(ForeignKey("monitor_projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(80))  # e-drivebook.com, k2drive.com…
    kind: Mapped[str] = mapped_column(String(10), server_default="production", default="production")  # production | test
    base_url: Mapped[str] = mapped_column(String(300))  # …/v1/monitoring/external
    # Encrypted with MONITORING_SECRET_KEY when it is set ("enc:" prefix), see monitoring.seal
    api_token: Mapped[str] = mapped_column(Text, server_default="", default="")  # empty = cannot be enabled
    webhook_secret: Mapped[str] = mapped_column(Text, server_default="", default="")  # empty = no webhook, e-mails from polling
    enabled: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    poll_interval_seconds: Mapped[int] = mapped_column(Integer, server_default="60", default=60)
    # State: unknown | up | degraded | down | off (API turned off there)
    state: Mapped[str] = mapped_column(String(10), server_default="unknown", default="unknown")
    status: Mapped[str] = mapped_column(String(10), server_default="")  # last "status" from /status
    fail_count: Mapped[int] = mapped_column(Integer, server_default="0", default=0)  # failed polls in a row
    last_poll_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_ok_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str] = mapped_column(Text, server_default="", default="")
    down_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    degraded_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    degraded_alerted: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    token_invalid: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)  # 401 e-mail sent
    snapshot: Mapped[str] = mapped_column(Text, server_default="", default="")  # last /status body (JSON)
    errors_cursor: Mapped[str] = mapped_column(String(40), server_default="", default="")  # since= for /errors
    errors_polled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MonitorEvent(Base):
    """History of an environment: state changes, e-mails, webhooks."""

    __tablename__ = "monitor_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    env_id: Mapped[int] = mapped_column(ForeignKey("monitor_envs.id", ondelete="CASCADE"), index=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    kind: Mapped[str] = mapped_column(String(10))  # state | mail | webhook | info
    text: Mapped[str] = mapped_column(Text)


class MonitorError(Base):
    """Error group reported by a project (one row per remote id; count grows)."""

    __tablename__ = "monitor_errors"
    __table_args__ = (UniqueConstraint("env_id", "remote_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    env_id: Mapped[int] = mapped_column(ForeignKey("monitor_envs.id", ondelete="CASCADE"), index=True)
    remote_id: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(20), server_default="")
    level: Mapped[str] = mapped_column(String(20), server_default="")
    logger_name: Mapped[str] = mapped_column(String(200), server_default="")
    message: Mapped[str] = mapped_column(Text, server_default="")
    traceback: Mapped[str] = mapped_column(Text, server_default="")
    path: Mapped[str] = mapped_column(String(500), server_default="")
    method: Mapped[str] = mapped_column(String(10), server_default="")
    user_id: Mapped[int | None] = mapped_column(Integer)
    count: Mapped[int] = mapped_column(Integer, server_default="1")
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    resolved: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    mailed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # our last e-mail about it
    via: Mapped[str] = mapped_column(String(8), server_default="poll")  # poll | webhook
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), default=utcnow, onupdate=utcnow)


class MonitorSettings(Base):
    """Single row: alert recipients (empty = MONITORING_ALERT_EMAILS from .env)."""

    __tablename__ = "monitor_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipients: Mapped[str] = mapped_column(Text, server_default="")
    seeded: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)  # first projects added once


class TelegramLink(Base):
    """Telegram chat of a panel user. While chat_id is empty, code_hash is a one-time link code."""

    __tablename__ = "telegram_links"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    chat_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)  # private chat = Telegram user id
    code_hash: Mapped[str] = mapped_column(String(64), server_default="", default="")
    code_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    linked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AssistantMessage(Base):
    """Assistant chat (panel page and Telegram share one history per user)."""

    __tablename__ = "assistant_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    role: Mapped[str] = mapped_column(String(10))  # user | assistant
    via: Mapped[str] = mapped_column(String(10), server_default="panel")  # panel | telegram
    engine: Mapped[str] = mapped_column(String(10), server_default="", default="")  # parser | claude | ""
    text: Mapped[str] = mapped_column(Text)
    # JSON list: [{"label", "kind": "undo" | "confirm", "method", "path", "body", "done"}]
    actions: Mapped[str] = mapped_column(Text, server_default="[]", default="[]")
