from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_db
from ..models import Board, BoardColumn, Card, User
from ..schemas import (
    BoardFull,
    BoardIn,
    BoardOut,
    BoardPatch,
    CardIn,
    CardOut,
    CardPatch,
    ColumnIn,
    ColumnOut,
    ColumnPatch,
)
from ..security import current_user

# Boards are shared by the whole team
router = APIRouter(tags=["kanban"], dependencies=[Depends(current_user)])


async def _get(db: AsyncSession, model, item_id: int):
    item = await db.get(model, item_id)
    if item is None:
        raise HTTPException(404, f"{model.__name__} not found")
    return item


async def _place(db: AsyncSession, model, parent, parent_id: int, item, index: int) -> None:
    """Insert item at index among its siblings and renumber positions."""
    siblings = list(
        (await db.scalars(select(model).where(parent == parent_id, model.id != item.id).order_by(model.position, model.id))).all()
    )
    siblings.insert(max(0, min(index, len(siblings))), item)
    for i, row in enumerate(siblings):
        row.position = i


async def _next_position(db: AsyncSession, model, parent, parent_id: int) -> int:
    return (await db.scalar(select(func.coalesce(func.max(model.position) + 1, 0)).where(parent == parent_id))) or 0


# Boards
@router.get("/boards", response_model=list[BoardOut])
async def list_boards(db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(Board).order_by(Board.position, Board.id))).all()


@router.post("/boards", response_model=BoardOut, status_code=201)
async def create_board(body: BoardIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    position = await db.scalar(select(func.coalesce(func.max(Board.position) + 1, 0)))
    board = Board(title=body.title.strip(), created_by=user.id, position=position or 0)
    board.columns = [BoardColumn(title=t.strip()[:120], position=i) for i, t in enumerate(body.columns) if t.strip()]
    db.add(board)
    await db.commit()
    return board


@router.get("/boards/{board_id}", response_model=BoardFull)
async def get_board(board_id: int, db: AsyncSession = Depends(get_db)):
    board = await db.scalar(
        select(Board).where(Board.id == board_id).options(selectinload(Board.columns).selectinload(BoardColumn.cards))
    )
    if board is None:
        raise HTTPException(404, "Board not found")
    return board


@router.patch("/boards/{board_id}", response_model=BoardOut)
async def rename_board(board_id: int, body: BoardPatch, db: AsyncSession = Depends(get_db)):
    board = await _get(db, Board, board_id)
    board.title = body.title.strip()
    await db.commit()
    return board


@router.delete("/boards/{board_id}", status_code=204)
async def delete_board(board_id: int, db: AsyncSession = Depends(get_db)):
    await db.delete(await _get(db, Board, board_id))
    await db.commit()


# Columns
@router.post("/boards/{board_id}/columns", response_model=ColumnOut, status_code=201)
async def create_column(board_id: int, body: ColumnIn, db: AsyncSession = Depends(get_db)):
    await _get(db, Board, board_id)
    column = BoardColumn(
        board_id=board_id, title=body.title.strip(), position=await _next_position(db, BoardColumn, BoardColumn.board_id, board_id)
    )
    db.add(column)
    await db.commit()
    return ColumnOut(id=column.id, title=column.title, position=column.position, cards=[])


@router.patch("/columns/{column_id}", response_model=ColumnOut)
async def update_column(column_id: int, body: ColumnPatch, db: AsyncSession = Depends(get_db)):
    column = await _get(db, BoardColumn, column_id)
    if body.title is not None:
        column.title = body.title.strip()
    if body.position is not None:
        await _place(db, BoardColumn, BoardColumn.board_id, column.board_id, column, body.position)
    await db.commit()
    return ColumnOut(id=column.id, title=column.title, position=column.position)


@router.delete("/columns/{column_id}", status_code=204)
async def delete_column(column_id: int, db: AsyncSession = Depends(get_db)):
    await db.delete(await _get(db, BoardColumn, column_id))
    await db.commit()


# Cards
@router.post("/columns/{column_id}/cards", response_model=CardOut, status_code=201)
async def create_card(column_id: int, body: CardIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await _get(db, BoardColumn, column_id)
    card = Card(
        column_id=column_id,
        title=body.title.strip(),
        description=body.description,
        assignee_id=body.assignee_id,
        created_by=user.id,
        position=await _next_position(db, Card, Card.column_id, column_id),
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


@router.patch("/cards/{card_id}", response_model=CardOut)
async def update_card(card_id: int, body: CardPatch, db: AsyncSession = Depends(get_db)):
    card = await _get(db, Card, card_id)
    sent = body.model_fields_set
    if body.title is not None:
        card.title = body.title.strip()
    if body.description is not None:
        card.description = body.description
    if "assignee_id" in sent:
        if body.assignee_id is not None:
            await _get(db, User, body.assignee_id)
        card.assignee_id = body.assignee_id
    if body.column_id is not None and body.column_id != card.column_id:
        target = await _get(db, BoardColumn, body.column_id)
        source = await _get(db, BoardColumn, card.column_id)
        if target.board_id != source.board_id:
            raise HTTPException(400, "Column belongs to another board")
        card.column_id = target.id
        if body.position is None:
            card.position = await _next_position(db, Card, Card.column_id, target.id)
    if body.position is not None:
        await _place(db, Card, Card.column_id, card.column_id, card, body.position)
    await db.commit()
    await db.refresh(card)
    return card


@router.delete("/cards/{card_id}", status_code=204)
async def delete_card(card_id: int, db: AsyncSession = Depends(get_db)):
    await db.delete(await _get(db, Card, card_id))
    await db.commit()
