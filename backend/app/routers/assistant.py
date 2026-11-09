import asyncio
import json
import shutil

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import assistant, mcp_panel, telegram
from ..config import settings
from ..db import get_db
from ..models import AssistantChat, AssistantMessage, User
from ..schemas import (
    AssistantActionIn, AssistantActionOut, AssistantIn, AssistantSendOut, AssistantStatus, ChatIn, ChatMessagesOut, ChatOut, ChatPatch,
)
from ..security import current_user

# Assistant and chats of the panel (the same chats as in Telegram) and linking Telegram in Settings
router = APIRouter(prefix="/assistant", tags=["assistant"])

WAIT = 25  # seconds the send request waits for the answer; longer answers are polled
_tasks: set[asyncio.Task] = set()


@router.get("", response_model=AssistantStatus)
async def status(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return AssistantStatus(
        telegram=telegram.configured(), telegram_linked=await telegram.chat_of(db, user.id) is not None,
        bot=await telegram.bot_username() if telegram.configured() else None,
        parser=bool(settings.assistant_node and shutil.which(settings.assistant_node) and assistant.PARSER.exists()),
        claude=assistant.claude_ready(user), model=settings.assistant_model, chat_model=settings.assistant_chat_model,
        models=list(assistant.MODELS), sandbox=assistant.sandbox(),
    )


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


# ===== Chats =====
def chat_out(c: AssistantChat) -> ChatOut:
    return ChatOut(id=c.id, kind=c.kind, title=c.title, model=assistant.model_of(c), own_model=c.model, busy=assistant.busy(c.id), updated_at=c.updated_at)


async def _own(db: AsyncSession, user: User, chat_id: int) -> AssistantChat:
    chat = await assistant.chat_of(db, user, chat_id)
    if chat is None:
        raise HTTPException(404, "Chat not found")
    return chat


@router.get("/chats", response_model=list[ChatOut])
async def chats(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return [chat_out(c) for c in await assistant.chats_of(db, user)]


@router.post("/chats", response_model=ChatOut, status_code=201)
async def create_chat(body: ChatIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return chat_out(await assistant.new_chat(db, user, body.title, body.model))


@router.patch("/chats/{chat_id}", response_model=ChatOut)
async def edit_chat(chat_id: int, body: ChatPatch, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    chat = await _own(db, user, chat_id)
    if body.title is not None and chat.kind == "chat":
        chat.title = body.title.strip()
    if body.model is not None:
        chat.model = body.model
    await db.commit()
    return chat_out(chat)


@router.delete("/chats/{chat_id}", status_code=204)
async def delete_chat(chat_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    chat = await _own(db, user, chat_id)
    if chat.kind == "assistant":
        raise HTTPException(400, "The assistant chat can only be cleared")
    await db.execute(delete(AssistantMessage).where(AssistantMessage.chat_id == chat.id))
    await db.delete(chat)
    await db.commit()


@router.get("/chats/{chat_id}/messages", response_model=ChatMessagesOut)
async def messages(chat_id: int, limit: int = Query(100, ge=1, le=300), user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    chat = await _own(db, user, chat_id)
    rows = (await db.scalars(
        select(AssistantMessage).where(AssistantMessage.chat_id == chat.id).order_by(AssistantMessage.id.desc()).limit(limit)
    )).all()
    return ChatMessagesOut(busy=assistant.busy(chat.id), messages=[assistant.out(m) for m in reversed(rows)])


@router.post("/chats/{chat_id}/messages", response_model=AssistantSendOut, status_code=201)
async def ask(chat_id: int, body: AssistantIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Stores the question and answers it in the background; quick answers come back here, long ones are polled."""
    chat = await _own(db, user, chat_id)
    asked = await assistant.ask(db, user, chat, body.text, "panel")
    task = asyncio.create_task(assistant.answer_later(user.id, chat.id, asked.id, late_after=WAIT))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    done, _ = await asyncio.wait({task}, timeout=WAIT)
    return AssistantSendOut(question=assistant.out(asked), answer=task.result() if task in done else None)


@router.delete("/chats/{chat_id}/messages", status_code=204)
async def clear(chat_id: int, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    chat = await _own(db, user, chat_id)
    await db.execute(delete(AssistantMessage).where(AssistantMessage.chat_id == chat.id))
    chat.session = ""  # Claude forgets the conversation too
    await db.commit()


@router.post("/messages/{message_id}/actions/{index}", response_model=AssistantActionOut)
async def act(message_id: int, index: int, body: AssistantActionIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    m, result = await assistant.run_action(db, user, message_id, index, body.accept)
    if m is None:
        raise HTTPException(404, "Message not found")
    return AssistantActionOut(message=assistant.out(m), result=result)


# ===== Panel tools for the sandbox container (MCP over HTTP) =====
# No login cookie: the key in the URL exists only while that user's Claude run lasts.
@router.post("/mcp/{key}", include_in_schema=False)
async def mcp(key: str, request: Request):
    run = assistant.SANDBOX_RUNS.get(key)
    if run is None:
        raise HTTPException(404, "Unknown run")
    try:
        msg = json.loads(await request.body())
    except ValueError:
        return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}, 400)
    batch = msg if isinstance(msg, list) else [msg]

    def work() -> list[dict]:
        token = mcp_panel.RUN.set(run)
        try:
            return [r for m in batch if isinstance(m, dict) and (r := mcp_panel.handle(m)) is not None]
        finally:
            mcp_panel.RUN.reset(token)

    replies = await asyncio.to_thread(work)
    if not replies:
        return Response(status_code=202)  # only notifications
    return JSONResponse(replies if isinstance(msg, list) else replies[0])


@router.get("/mcp/{key}", include_in_schema=False)
async def mcp_stream(key: str):
    return Response(status_code=405)  # no server-sent events: every answer comes with its request
