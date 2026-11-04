import datetime as dt
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
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
