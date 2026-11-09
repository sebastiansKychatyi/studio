"""Telegram bot of the panel: notifications (same kinds and quiet hours as Web Push) and the assistant.

Each panel user links their own private chat with a one-time code from Settings (t.me/<bot>?start=<code>);
messages from chats that are not linked are only answered with how to link. Long polling (getUpdates),
so no public webhook URL is needed; runs inside the API process like the push scheduler.
"""

import asyncio
import hashlib
import html
import json
import logging
import secrets
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import SessionLocal
from .models import Alarm, PushLater, TelegramLink, User
from .sync import utcnow

log = logging.getLogger("telegram")

CODE_TTL = timedelta(minutes=15)
SNOOZE = timedelta(minutes=10)
LIMIT = 4000  # Telegram allows 4096 characters

TEXT = {
    "sk": {
        "linked": "Hotovo ✅ Tento chat je prepojený s panelom ({name}). Sem budú chodiť upozornenia a môžeš mi písať, napr. „káva 3,5 €“ alebo „zajtra 14:00 hovor s Annou“.",
        "badCode": "Kód neplatí alebo vypršal. V paneli otvor Nastavenia → Telegram → Pripojiť.",
        "notLinked": "Tento chat nie je prepojený. V paneli otvor Nastavenia → Telegram → Pripojiť.",
        "taken": "Tento Telegram je už prepojený s iným účtom panela.",
        "help": "Napíš, čo pridať: výdavok, príjem, udalosť, úlohu, budík, termín, klienta… Alebo sa opýtaj, napr. „čo mám zajtra?“. /unlink — odpojiť tento chat.",
        "unlinked": "Chat je odpojený. Upozornenia sem už nebudú chodiť.", "onlyText": "Zatiaľ rozumiem len textu.",
        "undo": "↩️ Vrátiť", "yes": "✅ Áno", "no": "✖ Nie", "open": "Otvoriť", "snooze": "😴 O 10 min", "snoozed": "Pripomeniem o 10 minút",
    },
    "cs": {
        "linked": "Hotovo ✅ Tento chat je propojený s panelem ({name}). Sem budou chodit upozornění a můžeš mi psát, např. „káva 3,5 €“ nebo „zítra 14:00 hovor s Annou“.",
        "badCode": "Kód neplatí nebo vypršel. V panelu otevři Nastavení → Telegram → Připojit.",
        "notLinked": "Tento chat není propojený. V panelu otevři Nastavení → Telegram → Připojit.",
        "taken": "Tento Telegram je už propojený s jiným účtem panelu.",
        "help": "Napiš, co přidat: výdaj, příjem, událost, úkol, budík, termín, klienta… Nebo se zeptej, např. „co mám zítra?“. /unlink — odpojit tento chat.",
        "unlinked": "Chat je odpojený. Upozornění sem už chodit nebudou.", "onlyText": "Zatím rozumím jen textu.",
        "undo": "↩️ Vrátit", "yes": "✅ Ano", "no": "✖ Ne", "open": "Otevřít", "snooze": "😴 Za 10 min", "snoozed": "Připomenu za 10 minut",
    },
    "uk": {
        "linked": "Готово ✅ Цей чат підключено до панелі ({name}). Сюди приходитимуть сповіщення, і можна писати мені, напр. «кава 3,5 €» або «завтра 14:00 дзвінок з Анною».",
        "badCode": "Код недійсний або прострочений. У панелі відкрий Налаштування → Telegram → Підключити.",
        "notLinked": "Цей чат не підключено. У панелі відкрий Налаштування → Telegram → Підключити.",
        "taken": "Цей Telegram уже підключено до іншого акаунта панелі.",
        "help": "Напиши, що додати: витрату, дохід, подію, завдання, будильник, дедлайн, клієнта… Або спитай, напр. «що в мене завтра?». /unlink — відключити цей чат.",
        "unlinked": "Чат відключено. Сповіщення сюди більше не приходитимуть.", "onlyText": "Поки що розумію лише текст.",
        "undo": "↩️ Скасувати", "yes": "✅ Так", "no": "✖ Ні", "open": "Відкрити", "snooze": "😴 Через 10 хв", "snoozed": "Нагадаю через 10 хвилин",
    },
    "en": {
        "linked": "Done ✅ This chat is linked to the panel ({name}). Notifications come here, and you can write to me, e.g. “coffee 3.5 €” or “tomorrow 14:00 call with Anna”.",
        "badCode": "The code is not valid or has expired. In the panel open Settings → Telegram → Connect.",
        "notLinked": "This chat is not linked. In the panel open Settings → Telegram → Connect.",
        "taken": "This Telegram is already linked to another panel account.",
        "help": "Tell me what to add: expense, income, event, task, alarm, deadline, client… Or ask, e.g. “what do I have tomorrow?”. /unlink — disconnect this chat.",
        "unlinked": "Chat disconnected. No more notifications here.", "onlyText": "For now I understand text only.",
        "undo": "↩️ Undo", "yes": "✅ Yes", "no": "✖ No", "open": "Open", "snooze": "😴 In 10 min", "snoozed": "I will remind you in 10 minutes",
    },
}


def configured() -> bool:
    return bool(settings.telegram_bot_token)


# ===== Bot API =====
def call(method: str, params: dict | None = None, timeout: int = 20) -> Any:
    """Blocking Bot API call (run in a thread). Returns "result" or None. Tests replace it."""
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{settings.telegram_bot_token}/{method}",
        data=json.dumps(params or {}, ensure_ascii=False).encode(), headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
            return data.get("result") if data.get("ok") else None
    except urllib.error.HTTPError as e:
        log.warning("telegram %s: HTTP %s %s", method, e.code, e.read()[:200])
    except Exception as e:  # noqa: BLE001 - network problems must not stop the bot
        log.warning("telegram %s: %s", method, e)
    return None


Call = Callable[[str, dict | None], Any]
_username: str | None = None


async def bot_username(api: Call = call) -> str | None:
    global _username
    if _username is None and configured():
        me = await asyncio.to_thread(api, "getMe", None)
        _username = (me or {}).get("username")
    return _username


def keyboard(rows: list[list[dict]]) -> dict | None:
    rows = [r for r in rows if r]
    return {"inline_keyboard": rows} if rows else None


async def send(chat_id: int, text: str, markup: dict | None = None, api: Call = call) -> bool:
    chunks = [text[i:i + LIMIT] for i in range(0, len(text), LIMIT)] or [""]
    ok = True
    for i, chunk in enumerate(chunks):
        params = {"chat_id": chat_id, "text": chunk, "parse_mode": "HTML", "disable_web_page_preview": True}
        if markup and i == len(chunks) - 1:
            params["reply_markup"] = markup
        ok = await asyncio.to_thread(api, "sendMessage", params) is not None and ok
    return ok


# ===== Linking =====
def _sha(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


async def link_url(db: AsyncSession, user_id: int, api: Call = call) -> str | None:
    """New one-time link for Settings → Connect (replaces an unused one)."""
    name = await bot_username(api)
    if not name:
        return None
    code = secrets.token_urlsafe(18)
    row = await db.get(TelegramLink, user_id) or TelegramLink(user_id=user_id)
    row.code_hash, row.code_expires = _sha(code), utcnow() + CODE_TTL
    db.add(row)
    await db.commit()
    return f"https://t.me/{name}?start={code}"


async def chat_of(db: AsyncSession, user_id: int) -> int | None:
    row = await db.get(TelegramLink, user_id)
    return row.chat_id if row else None


async def unlink(db: AsyncSession, user_id: int) -> None:
    row = await db.get(TelegramLink, user_id)
    if row:
        await db.delete(row)
        await db.commit()


async def _link(db: AsyncSession, chat_id: int, code: str) -> tuple[User | None, str]:
    row = await db.scalar(select(TelegramLink).where(TelegramLink.code_hash == _sha(code)))
    expires = row.code_expires if row else None
    if expires is not None and expires.tzinfo is None:  # SQLite returns naive UTC
        expires = expires.replace(tzinfo=timezone.utc)
    if row is None or expires is None or expires < utcnow():
        return None, "badCode"
    other = await db.scalar(select(TelegramLink).where(TelegramLink.chat_id == chat_id, TelegramLink.user_id != row.user_id))
    if other is not None:
        return None, "taken"
    row.chat_id, row.code_hash, row.code_expires, row.linked_at = chat_id, "", None, utcnow()
    await db.commit()
    return await db.get(User, row.user_id), "linked"


async def _user_of_chat(db: AsyncSession, chat_id: int) -> User | None:
    return await db.scalar(select(User).join(TelegramLink, TelegramLink.user_id == User.id).where(TelegramLink.chat_id == chat_id))


# ===== Notifications =====
def push_message(payload: dict, t: dict, alarm: bool) -> tuple[str, dict | None]:
    """Web Push payload → Telegram text and buttons."""
    text = f"<b>{html.escape(str(payload.get('title') or ''))}</b>"
    if payload.get("body"):
        text += f"\n{html.escape(str(payload['body']))}"
    buttons = []
    if alarm and (payload.get("alarm") or {}).get("id"):
        buttons.append({"text": t["snooze"], "callback_data": f"z:{payload['alarm']['id']}"})
    site = settings.site_url.rstrip("/")
    if site.startswith("https://") and str(payload.get("url") or "").startswith("/"):
        buttons.append({"text": t["open"], "url": site + payload["url"]})
    return text, keyboard([buttons])


async def notify(chat_id: int, payload: dict, lang: str, kind: str, api: Call = call) -> int:
    text, markup = push_message(payload, TEXT[lang], kind == "alarms")
    return int(await send(chat_id, text, markup, api))


async def broadcast(db: AsyncSession, user_ids: list[int], text: str, api: Call = call) -> int:
    """Plain text to these users' chats (monitoring alerts)."""
    if not configured() or not user_ids:
        return 0
    chats = (await db.scalars(select(TelegramLink.chat_id).where(TelegramLink.user_id.in_(user_ids), TelegramLink.chat_id.is_not(None)))).all()
    return sum([await send(c, html.escape(text), None, api) for c in chats])


# ===== Updates =====
def action_buttons(message_id: int, actions: list[dict], t: dict) -> dict | None:
    rows = []
    for i, a in enumerate(actions):
        if a.get("done"):
            continue
        if a["kind"] == "undo":
            rows.append([{"text": f"{t['undo']} {a['label'] if a['label'] != 'undo' else ''}".strip()[:60], "callback_data": f"a:{message_id}:{i}"}])
        else:
            rows.append([{"text": f"{t['yes']}: {a['label']}"[:60], "callback_data": f"a:{message_id}:{i}"},
                         {"text": t["no"], "callback_data": f"n:{message_id}:{i}"}])
    return keyboard(rows)


async def _lang(db: AsyncSession, user: User | None, tg_lang: str | None) -> str:
    from .notify import LANGS, lang_of, prefs_of  # notify imports this module

    if user is not None:
        return lang_of(await prefs_of(db, user.id))
    code = (tg_lang or "")[:2]
    return code if code in LANGS else ("uk" if code == "ru" else "sk")


async def handle_update(db: AsyncSession, upd: dict, api: Call = call) -> None:
    from . import assistant

    if "callback_query" in upd:
        await _callback(db, upd["callback_query"], api)
        return
    msg = upd.get("message") or {}
    chat = msg.get("chat") or {}
    if chat.get("type") != "private":
        return  # groups are ignored: one private chat per user
    chat_id, text = chat["id"], (msg.get("text") or "").strip()
    user = await _user_of_chat(db, chat_id)
    t = TEXT[await _lang(db, user, (msg.get("from") or {}).get("language_code"))]

    if text.startswith("/start"):
        code = text[6:].strip()
        if code:
            user, key = await _link(db, chat_id, code)
            t = TEXT[await _lang(db, user, None)] if user else t
            await send(chat_id, t[key].format(name=html.escape(user.name or user.username)) if user else t[key], None, api)
        else:
            await send(chat_id, t["help"] if user else t["notLinked"], None, api)
        return
    if user is None:
        await send(chat_id, t["notLinked"], None, api)
        return
    if text in ("/unlink", "/stop"):
        await unlink(db, user.id)
        await send(chat_id, t["unlinked"], None, api)
        return
    if text == "/help":
        await send(chat_id, t["help"], None, api)
        return
    if not text:
        await send(chat_id, t["onlyText"], None, api)
        return
    await asyncio.to_thread(api, "sendChatAction", {"chat_id": chat_id, "action": "typing"})
    answer = await assistant.handle(db, user, text, "telegram")
    await send(chat_id, html.escape(answer.text), action_buttons(answer.id, json.loads(answer.actions), t), api)


async def _callback(db: AsyncSession, q: dict, api: Call) -> None:
    from . import assistant, notify as push

    chat_id = ((q.get("message") or {}).get("chat") or {}).get("id")
    user = await _user_of_chat(db, chat_id) if chat_id else None
    t = TEXT[await _lang(db, user, None)]
    data, note = str(q.get("data") or ""), ""
    parts = data.split(":")
    if user is not None and parts[0] in ("a", "n") and len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
        _, mid, idx = parts
        m, note = await assistant.run_action(db, user, int(mid), int(idx), data[0] == "a")
        if m is not None:
            markup = action_buttons(m.id, json.loads(m.actions), t) or {"inline_keyboard": []}
            await asyncio.to_thread(api, "editMessageReplyMarkup", {"chat_id": chat_id, "message_id": q["message"]["message_id"], "reply_markup": markup})
    elif user is not None and parts[0] == "z" and len(parts) == 2 and parts[1].isdigit():
        alarm = await db.get(Alarm, int(parts[1]))
        if alarm is not None and alarm.user_id == user.id:
            lang = await _lang(db, user, None)
            payload = push.alarm_payload(push.TEXT[lang], lang, alarm.id, alarm.time, alarm.label)
            db.add(PushLater(user_id=user.id, fire_at=utcnow() + SNOOZE, payload=json.dumps(payload, ensure_ascii=False)))
            await db.commit()
            note = t["snoozed"]
    await asyncio.to_thread(api, "answerCallbackQuery", {"callback_query_id": q.get("id"), "text": note[:190]})


async def run_bot() -> None:
    """Long polling; each update in its own session so a slow Claude answer does not block others."""
    await asyncio.to_thread(call, "deleteWebhook", None)
    offset, running = 0, set()

    async def one(upd: dict) -> None:
        try:
            async with SessionLocal() as db:
                await handle_update(db, upd)
        except Exception:  # noqa: BLE001 - keep the bot alive
            log.exception("telegram update")

    while True:
        params = {"offset": offset, "timeout": 50, "allowed_updates": ["message", "callback_query"]}
        updates = await asyncio.to_thread(call, "getUpdates", params, 60)
        if updates is None:
            await asyncio.sleep(5)
            continue
        for upd in updates:
            offset = max(offset, upd["update_id"] + 1)
            task = asyncio.create_task(one(upd))
            running.add(task)
            task.add_done_callback(running.discard)
