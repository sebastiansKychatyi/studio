from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    columns: Mapped[list["BoardColumn"]] = relationship(
        back_populates="board", order_by="BoardColumn.position", cascade="all, delete-orphan", passive_deletes=True
    )


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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Expense(MoneyEntry, Base):
    __tablename__ = "expenses"


class Income(MoneyEntry, Base):
    __tablename__ = "incomes"
