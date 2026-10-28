import re
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_db
from ..models import Board, BoardColumn, Card, User
from ..schemas import (
    BoardFull,
    BoardIn,
    BoardListItem,
    BoardOut,
    BoardPatch,
    CardIn,
    CardOut,
    CardPatch,
    ColumnIn,
    ColumnOut,
    ColumnPatch,
    MentionOut,
)
from ..security import current_user

# Team boards are shared; private boards and private cards are visible only to their creator
router = APIRouter(tags=["kanban"])


def can_see_board(board: Board, user: User) -> bool:
    return not board.is_private or board.created_by in (user.id, None)


def can_see_card(card: Card, user: User) -> bool:
    return not card.is_private or card.created_by in (user.id, None)


def _owner_only(item: Board | Card, user: User) -> None:
    if item.created_by not in (user.id, None):
        raise HTTPException(403, "Only the creator can change visibility")


async def _board(db: AsyncSession, board_id: int, user: User) -> Board:
    board = await db.get(Board, board_id)
    if board is None or not can_see_board(board, user):
        raise HTTPException(404, "Board not found")
    return board


async def _column(db: AsyncSession, column_id: int, user: User) -> BoardColumn:
    column = await db.get(BoardColumn, column_id)
    if column is None:
        raise HTTPException(404, "Column not found")
    await _board(db, column.board_id, user)
    return column


async def _card(db: AsyncSession, card_id: int, user: User) -> Card:
    card = await db.get(Card, card_id)
    if card is None or not can_see_card(card, user):
        raise HTTPException(404, "Card not found")
    await _column(db, card.column_id, user)
    return card


async def _place(db: AsyncSession, model, where, item, index: int, visible: Callable | None = None) -> None:
    """Move item to `index` among the siblings the user sees, keep hidden ones in place, renumber positions."""
    siblings = list((await db.scalars(select(model).where(where, model.id != item.id).order_by(model.position, model.id))).all())
    shown = [i for i, row in enumerate(siblings) if visible is None or visible(row)]
    index = max(0, index)
    at = shown[index] if index < len(shown) else (shown[-1] + 1 if shown else len(siblings))
    siblings.insert(at, item)
    for i, row in enumerate(siblings):
        row.position = i


async def _next_position(db: AsyncSession, model, where) -> int:
    return (await db.scalar(select(func.coalesce(func.max(model.position) + 1, 0)).where(where))) or 0


async def _no_hidden_cards(db: AsyncSession, user: User, where) -> None:
    """Refuse to delete a column/board that holds a teammate's private cards."""
    hidden = await db.scalar(
        select(func.count()).select_from(Card).join(BoardColumn).where(where, Card.is_private, Card.created_by != user.id)
    )
    if hidden:
        raise HTTPException(409, "Contains private cards of another user")


# Boards
@router.get("/boards", response_model=list[BoardListItem])
async def list_boards(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    boards = (await db.scalars(select(Board).options(selectinload(Board.columns)).order_by(Board.position, Board.id))).all()
    return [b for b in boards if can_see_board(b, user)]


@router.post("/boards", response_model=BoardOut, status_code=201)
async def create_board(body: BoardIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    position = await _next_position(db, Board, Board.id.isnot(None))
    board = Board(title=body.title.strip(), created_by=user.id, position=position, is_private=body.is_private)
    board.columns = [BoardColumn(title=t.strip()[:120], position=i) for i, t in enumerate(body.columns) if t.strip()]
    db.add(board)
    await db.commit()
    return board


@router.get("/boards/{board_id}", response_model=BoardFull)
async def get_board(board_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    board = await db.scalar(
        select(Board).where(Board.id == board_id).options(selectinload(Board.columns).selectinload(BoardColumn.cards))
    )
    if board is None or not can_see_board(board, user):
        raise HTTPException(404, "Board not found")
    # Hide the teammate's private cards (response only, ORM objects untouched)
    full = BoardFull.model_validate(board)
    for column in full.columns:
        column.cards = [c for c in column.cards if not c.is_private or c.created_by in (user.id, None)]
    return full


@router.patch("/boards/{board_id}", response_model=BoardOut)
async def update_board(board_id: int, body: BoardPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    board = await _board(db, board_id, user)
    if body.title is not None:
        board.title = body.title.strip()
    if body.is_private is not None and body.is_private != board.is_private:
        _owner_only(board, user)
        if body.is_private:
            # Board becomes invisible to the teammate together with all their cards
            await _no_hidden_cards(db, user, BoardColumn.board_id == board.id)
            others = await db.scalar(
                select(func.count()).select_from(Card).join(BoardColumn).where(BoardColumn.board_id == board.id, Card.created_by != user.id)
            )
            if others:
                raise HTTPException(409, "Board has cards of another user")
        board.is_private = body.is_private
    if body.position is not None:
        await _place(db, Board, Board.id.isnot(None), board, body.position, lambda b: can_see_board(b, user))
    await db.commit()
    return board


@router.delete("/boards/{board_id}", status_code=204)
async def delete_board(board_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    board = await _board(db, board_id, user)
    await _no_hidden_cards(db, user, BoardColumn.board_id == board.id)
    await db.delete(board)
    await db.commit()


# Columns
@router.post("/boards/{board_id}/columns", response_model=ColumnOut, status_code=201)
async def create_column(board_id: int, body: ColumnIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await _board(db, board_id, user)
    column = BoardColumn(
        board_id=board_id, title=body.title.strip(), position=await _next_position(db, BoardColumn, BoardColumn.board_id == board_id)
    )
    db.add(column)
    await db.commit()
    return ColumnOut(id=column.id, title=column.title, position=column.position, cards=[])


@router.patch("/columns/{column_id}", response_model=ColumnOut)
async def update_column(column_id: int, body: ColumnPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    column = await _column(db, column_id, user)
    if body.title is not None:
        column.title = body.title.strip()
    if body.position is not None:
        await _place(db, BoardColumn, BoardColumn.board_id == column.board_id, column, body.position)
    await db.commit()
    return ColumnOut(id=column.id, title=column.title, position=column.position)


@router.delete("/columns/{column_id}", status_code=204)
async def delete_column(column_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    column = await _column(db, column_id, user)
    await _no_hidden_cards(db, user, BoardColumn.id == column.id)
    await db.delete(column)
    await db.commit()


# Cards
@router.post("/columns/{column_id}/cards", response_model=CardOut, status_code=201)
async def create_card(column_id: int, body: CardIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await _column(db, column_id, user)
    card = Card(
        column_id=column_id,
        title=body.title.strip(),
        description=body.description,
        assignee_id=body.assignee_id,
        due_date=body.due_date,
        is_private=body.is_private,
        created_by=user.id,
        position=await _next_position(db, Card, Card.column_id == column_id),
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


@router.patch("/cards/{card_id}", response_model=CardOut)
async def update_card(card_id: int, body: CardPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    card = await _card(db, card_id, user)
    sent = body.model_fields_set
    if body.title is not None:
        card.title = body.title.strip()
    if body.description is not None:
        card.description = body.description
    if "assignee_id" in sent:
        if body.assignee_id is not None and await db.get(User, body.assignee_id) is None:
            raise HTTPException(404, "User not found")
        card.assignee_id = body.assignee_id
    if "due_date" in sent:
        card.due_date = body.due_date
    if body.is_private is not None and body.is_private != card.is_private:
        _owner_only(card, user)
        card.is_private = body.is_private
    # Any column the user can see, also on another board
    if body.column_id is not None and body.column_id != card.column_id:
        target = await _column(db, body.column_id, user)
        board = await db.get(Board, target.board_id)
        if board.is_private and card.created_by not in (user.id, None):
            raise HTTPException(409, "Card of another user cannot go to a private board")
        card.column_id = target.id
        if body.position is None:
            card.position = await _next_position(db, Card, Card.column_id == target.id)
    if body.position is not None:
        await _place(db, Card, Card.column_id == card.column_id, card, body.position, lambda c: can_see_card(c, user))
    await db.commit()
    await db.refresh(card)
    return card


@router.delete("/cards/{card_id}", status_code=204)
async def delete_card(card_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.delete(await _card(db, card_id, user))
    await db.commit()


# Mentions: open cards (not in the last column) that @mention the user or are assigned to them
@router.get("/mentions", response_model=list[MentionOut])
async def mentions(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    tag = re.compile(rf"@{re.escape(user.username)}(?![\w.-])", re.IGNORECASE)
    boards = (await db.scalars(select(Board).options(selectinload(Board.columns).selectinload(BoardColumn.cards)))).all()
    out = []
    for board in boards:
        if not can_see_board(board, user):
            continue
        for column in board.columns[:-1]:
            for card in column.cards:
                if not can_see_card(card, user):
                    continue
                if card.assignee_id == user.id or tag.search(f"{card.title}\n{card.description}"):
                    out.append(
                        MentionOut(
                            **CardOut.model_validate(card).model_dump(),
                            board_id=board.id,
                            board_title=board.title,
                            column_title=column.title,
                        )
                    )
    # Nearest deadline first, then newest
    out.sort(key=lambda c: (c.due_date is None, c.due_date or c.updated_at.date(), -c.id))
    return out
