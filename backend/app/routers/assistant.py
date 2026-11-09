import asyncio
import shutil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import assistant, monitoring, telegram
from ..config import settings
from ..db import get_db
from ..models import AssistantMessage, ClaudeLogin, User
from ..schemas import AssistantActionIn, AssistantActionOut, AssistantIn, AssistantMessageOut, AssistantStatus, ClaudeLoginIn
from ..security import current_user

# Assistant chat of the panel (same history as the Telegram chat) and linking Telegram in Settings
router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.get("", response_model=AssistantStatus)
async def status(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    own = await db.get(ClaudeLogin, user.id)
    return AssistantStatus(
        telegram=telegram.configured(), telegram_linked=await telegram.chat_of(db, user.id) is not None,
        bot=await telegram.bot_username() if telegram.configured() else None,
        parser=bool(settings.assistant_node and shutil.which(settings.assistant_node) and assistant.PARSER.exists()),
        claude=assistant.claude_ready(user, await assistant.claude_login(db, user)),
        claude_source="own" if own else "server" if assistant.claude_home(user) else None,
        claude_hint=own.hint if own else "", model=settings.assistant_model,
    )


@router.put("/claude", status_code=204)
async def claude_connect(body: ClaudeLoginIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Own Claude for the assistant: `claude setup-token` or an API key. Tried once before it is saved."""
    token = body.token.strip()
    kind = assistant.token_kind(token)
    if kind is None:
        raise HTTPException(422, "Not a Claude token (sk-ant-…)")
    if not assistant.cli_available():
        raise HTTPException(503, "Claude CLI is not installed on the server")
    if reason := await asyncio.to_thread(assistant.check_claude, kind, token):
        raise HTTPException(400, f"Claude did not accept the token: {reason}")
    row = await db.get(ClaudeLogin, user.id) or ClaudeLogin(user_id=user.id)
    row.kind, row.secret, row.hint, row.added_at = kind, monitoring.seal(token), token[-4:], assistant.utcnow()
    db.add(row)
    await db.commit()


@router.delete("/claude", status_code=204)
async def claude_disconnect(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ClaudeLogin).where(ClaudeLogin.user_id == user.id))
    await db.commit()


@router.post("/telegram")
async def telegram_link(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)) -> dict:
    """One-time t.me link (15 min) that connects the chat that opens it to this account."""
    if not telegram.configured():
        raise HTTPException(404, "Telegram bot is not set up")
    url = await telegram.link_url(db, user.id)
    if url is None:
        raise HTTPException(502, "Telegram is not answering")
    return {"url": url}


@router.delete("/telegram", status_code=204)
async def telegram_unlink(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await telegram.unlink(db, user.id)


@router.get("/messages", response_model=list[AssistantMessageOut])
async def messages(limit: int = Query(50, ge=1, le=200), user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(
        select(AssistantMessage).where(AssistantMessage.user_id == user.id).order_by(AssistantMessage.id.desc()).limit(limit)
    )).all()
    return [assistant.out(m) for m in reversed(rows)]


@router.post("/messages", response_model=AssistantMessageOut, status_code=201)
async def ask(body: AssistantIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Answer of the assistant (the question is stored too; reload the list to show both)."""
    return assistant.out(await assistant.handle(db, user, body.text, "panel"))


@router.post("/messages/{message_id}/actions/{index}", response_model=AssistantActionOut)
async def act(message_id: int, index: int, body: AssistantActionIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    m, result = await assistant.run_action(db, user, message_id, index, body.accept)
    if m is None:
        raise HTTPException(404, "Message not found")
    return AssistantActionOut(message=assistant.out(m), result=result)


@router.delete("/messages", status_code=204)
async def clear(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(AssistantMessage).where(AssistantMessage.user_id == user.id))
    await db.commit()
