"""Assistant: one message (panel page or Telegram) → an action in the panel.

Our quick parser (app/utils/quickParse.ts, run by Node) goes first: no AI, instant, free. What it does
not understand goes to the Claude Code CLI with the user's own login (<ASSISTANT_CLAUDE_HOME>/<username>),
started without any built-in tool (no shell, no files) and with only our MCP server (mcp_panel.py).
Every action goes through this API as that user (short-lived session token), so the panel's own rules
decide what they may see and change. Created entries get an "Undo"; changes need a "Yes" first.
"""

import asyncio
import hashlib
import json
import logging
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import AssistantMessage, Client, Session, Subject, User
from .notify import LANGS, lang_of, prefs_of, tz_of
from .sync import utcnow

log = logging.getLogger("assistant")

ROOT = Path(__file__).resolve().parents[2]
PARSER = ROOT / "scripts" / "quick-parse-cli.mjs"
BACKEND = Path(__file__).resolve().parents[1]
CONFIDENT = 0.85  # parser results below go to Claude
HISTORY = timedelta(minutes=30)  # earlier messages are a new conversation
HISTORY_MAX = 10
TOKEN_MINUTES = 15

TEXT = {
    "sk": {
        "expense": "Výdavok", "income": "Príjem", "event": "Udalosť", "task": "Úloha", "alarm": "Budík", "work": "Termín",
        "today": "dnes", "noClaude": "Nerozumiem. Napíš to inak (napr. „káva 3,5 €“ alebo „zajtra 14:00 hovor s Annou“) — Claude ešte nie je pripojený.",
        "claudeFailed": "Claude teraz neodpovedá, skús to o chvíľu.", "noBoard": "Najprv vytvor nástenku pre úlohy.",
        "failed": "Nepodarilo sa uložiť", "undone": "Vrátené", "applied": "Hotovo", "declined": "Zrušené", "gone": "Táto akcia už neplatí",
    },
    "cs": {
        "expense": "Výdaj", "income": "Příjem", "event": "Událost", "task": "Úkol", "alarm": "Budík", "work": "Termín",
        "today": "dnes", "noClaude": "Nerozumím. Napiš to jinak (např. „káva 3,5 €“ nebo „zítra 14:00 hovor s Annou“) — Claude ještě není připojený.",
        "claudeFailed": "Claude teď neodpovídá, zkus to za chvíli.", "noBoard": "Nejdřív vytvoř nástěnku pro úkoly.",
        "failed": "Nepodařilo se uložit", "undone": "Vráceno", "applied": "Hotovo", "declined": "Zrušeno", "gone": "Tato akce už neplatí",
    },
    "uk": {
        "expense": "Витрата", "income": "Дохід", "event": "Подія", "task": "Завдання", "alarm": "Будильник", "work": "Дедлайн",
        "today": "сьогодні", "noClaude": "Не зрозумів. Напиши інакше (напр. «кава 3,5 €» або «завтра 14:00 дзвінок з Анною») — Claude ще не підключено.",
        "claudeFailed": "Claude зараз не відповідає, спробуй трохи пізніше.", "noBoard": "Спершу створи дошку для завдань.",
        "failed": "Не вдалося зберегти", "undone": "Скасовано", "applied": "Готово", "declined": "Відхилено", "gone": "Ця дія вже недійсна",
    },
    "en": {
        "expense": "Expense", "income": "Income", "event": "Event", "task": "Task", "alarm": "Alarm", "work": "Deadline",
        "today": "today", "noClaude": "I did not get that. Try e.g. “coffee 3.5 €” or “tomorrow 14:00 call with Anna” — Claude is not connected yet.",
        "claudeFailed": "Claude is not answering right now, try again in a moment.", "noBoard": "Create a board for tasks first.",
        "failed": "Could not save", "undone": "Undone", "applied": "Done", "declined": "Cancelled", "gone": "This action is no longer valid",
    },
}
assert set(TEXT) == set(LANGS)


@dataclass
class Reply:
    text: str
    engine: str = ""  # parser | claude | ""
    actions: list[dict] = field(default_factory=list)


# ===== Internal API, as the user =====
async def issue_token(db: AsyncSession, user_id: int) -> str:
    """Short-lived session for one assistant run (same cookie the panel uses)."""
    token = secrets.token_urlsafe(32)
    await db.execute(delete(Session).where(Session.expires_at < utcnow()))
    db.add(Session(token_hash=hashlib.sha256(token.encode()).hexdigest(), user_id=user_id, expires_at=utcnow() + timedelta(minutes=TOKEN_MINUTES)))
    await db.commit()
    return token


def api_call(token: str, method: str, path: str, body: dict | None = None) -> tuple[int, Any]:
    """Blocking request to this API (run in a thread). Tests replace it."""
    req = urllib.request.Request(
        f"{settings.internal_api_url.rstrip('/')}/api/team{path}", method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", "Cookie": f"{settings.cookie_name}={token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"null")
        except ValueError:
            return e.code, None
    except Exception as e:  # noqa: BLE001 - reported to the user as "could not save"
        return 0, str(e)


Caller = Callable[[str, str, str, dict | None], tuple[int, Any]]


# ===== Quick parser =====
def run_parser(text: str, ctx: dict) -> dict | None:
    """Blocking: the same parser as the panel's quick add. None = Node or the script is missing."""
    if not settings.assistant_node or not PARSER.exists():
        return None
    try:
        out = subprocess.run(
            [settings.assistant_node, "--experimental-strip-types", "--no-warnings", str(PARSER)],
            input=json.dumps({"text": text, "ctx": ctx}), capture_output=True, text=True, encoding="utf-8", timeout=10,
        )
        return json.loads(out.stdout) if out.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        log.exception("quick parser")
        return None


Parser = Callable[[str, dict], dict | None]


async def parser_ctx(db: AsyncSession, user: User, prefs: dict, today: date) -> dict:
    clients = (await db.scalars(select(Client).where(Client.user_id == user.id))).all()
    users = (await db.scalars(select(User))).all()
    subjects = (await db.scalars(select(Subject).where(Subject.user_id == user.id))).all()
    return {
        "today": today.isoformat(),
        "currency": prefs.get("currency") if prefs.get("currency") in ("EUR", "UAH", "USD") else "EUR",
        "clients": [{"id": c.id, "name": c.name, "company": c.company} for c in clients],
        "users": [{"id": u.id, "username": u.username, "name": u.name} for u in users],
        "subjects": [{"id": s.id, "name": s.name} for s in subjects],
    }


def confident(r: dict | None) -> bool:
    """Sure enough to save without asking: known kind, high confidence, required fields present."""
    if not r or not r.get("kind") or float(r.get("confidence") or 0) < CONFIDENT:
        return False
    need = {"expense": "amount", "income": "amount", "alarm": "time", "work": "date"}.get(r["kind"], "title")
    return r.get(need) not in (None, "")


def _money(n: float, cur: str) -> str:
    return f"{n:,.2f}".replace(",", " ").replace(".", ",") + {"EUR": " €", "USD": " $", "UAH": " ₴"}.get(cur, f" {cur}")


def summary(r: dict, t: dict, today: str) -> str:
    """One line about what the parser saved, like the quick add preview."""
    k = r["kind"]
    day = None if not r.get("date") or r.get("date") == today else ".".join(reversed(r["date"].split("-")[1:]))
    if k in ("expense", "income"):
        parts = [_money(float(r["amount"]), r.get("currency") or "EUR"), r.get("title"), day]
    elif k == "event":
        parts = [r.get("title"), f"{day or t['today']} {r.get('time') or ''}{'–' + r['end'] if r.get('end') else ''}".strip()]
    elif k == "alarm":
        parts = [r.get("time"), r.get("title")]
    else:
        parts = [r.get("title"), day]
    return f"{t[k]}: " + " · ".join(str(p) for p in parts if p)


async def _task_column(token: str, caller: Caller) -> int | None:
    code, boards = await asyncio.to_thread(caller, token, "GET", "/boards", None)
    if code != 200 or not boards:
        return None
    cols = boards[0].get("columns") or []
    return cols[0]["id"] if cols else None


async def save_parsed(r: dict, today: str, token: str, caller: Caller) -> tuple[int, dict | None, str]:
    """Same requests as the panel's quick add. Returns (HTTP status, created row, undo path)."""
    k = r["kind"]
    if k in ("expense", "income"):
        path = "/income" if k == "income" else "/expenses"
        body = {"amount": r["amount"], "currency": r.get("currency") or "EUR", "category": r.get("category") or "other",
                "note": r.get("title") or "", "spent_on": r.get("date") or today}
        if k == "income":
            body["client_id"] = r.get("client_id")
    elif k == "event":
        path, body = "/events", {"title": r["title"], "date": r.get("date") or today, "start": r.get("time") or "09:00",
                                 "end": r.get("end") or "10:00", "client_id": r.get("client_id")}
    elif k == "task":
        col = await _task_column(token, caller)
        if col is None:
            return 404, None, ""
        path, body = f"/columns/{col}/cards", {"title": r["title"], "due_date": r.get("date"), "assignee_id": r.get("assignee_id"), "client_id": r.get("client_id")}
    elif k == "alarm":
        path, body = "/alarms", {"time": r["time"], "label": r.get("title") or "", "days": r.get("days") or [], "enabled": True}
    else:
        path = "/study/works"
        body = {"title": r.get("title") or r.get("workKind") or "assignment", "kind": r.get("workKind") or "assignment",
                "due": r["date"], "due_time": r.get("time"), "subject_id": r.get("subject_id")}
    code, row = await asyncio.to_thread(caller, token, "POST", path, body)
    undo = {"expense": "/expenses", "income": "/income", "event": "/events", "task": "/cards", "alarm": "/alarms", "work": "/study/works"}[k]
    return code, row if isinstance(row, dict) else None, f"{undo}/{row['id']}" if isinstance(row, dict) and "id" in row else ""


# ===== Claude =====
def claude_home(user: User) -> Path | None:
    if not settings.assistant_claude_home:
        return None
    path = Path(settings.assistant_claude_home) / user.username.lower()
    return path if path.is_dir() else None


def claude_ready(user: User) -> bool:
    return bool(settings.assistant_claude and shutil.which(settings.assistant_claude) and claude_home(user))


def claude_args(mcp_config: str, system: str) -> list[str]:
    """No built-in tools at all, only our MCP server; anything else is refused without asking."""
    return [
        shutil.which(settings.assistant_claude) or settings.assistant_claude, "-p", "--output-format", "json", "--model", settings.assistant_model,
        "--tools", "", "--strict-mcp-config", "--mcp-config", mcp_config, "--allowedTools", "mcp__panel",
        "--permission-mode", "dontAsk", "--no-session-persistence", "--system-prompt", system,
    ]


def _child_env(home: Path) -> dict[str, str]:
    # Only what the CLI needs: no database URL or other secrets of this API
    keep = ("PATH", "HOME", "USERPROFILE", "SYSTEMROOT", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "LANG", "LC_ALL")
    return {**{k: os.environ[k] for k in keep if k in os.environ}, "CLAUDE_CONFIG_DIR": str(home)}


def run_claude(user: User, prompt: str, system: str, tool_env: dict[str, str]) -> tuple[str, list[dict]]:
    """Blocking: one Claude answer. Returns (text, actions the tools recorded). Raises on failure."""
    home = claude_home(user)
    if home is None:
        raise RuntimeError("no Claude login for this user")
    with tempfile.TemporaryDirectory(prefix="assistant-") as work:
        actions_file = Path(work) / "actions.jsonl"
        mcp = Path(work) / "mcp.json"
        mcp.write_text(json.dumps({"mcpServers": {"panel": {
            "command": sys.executable, "args": ["-m", "app.mcp_panel"],
            "env": {**tool_env, "PANEL_ACTIONS": str(actions_file), "PYTHONPATH": str(BACKEND), "PYTHONIOENCODING": "utf-8"},
        }}}), encoding="utf-8")
        run_dir = Path(work) / "cwd"  # empty: no project files or settings
        run_dir.mkdir()
        out = subprocess.run(
            claude_args(str(mcp), system), input=prompt, capture_output=True, text=True, encoding="utf-8",
            timeout=settings.assistant_timeout, cwd=run_dir, env=_child_env(home),
        )
        try:
            result = json.loads(out.stdout)
        except ValueError:
            raise RuntimeError(f"claude exit {out.returncode}: {out.stderr[-300:]}") from None
        if result.get("is_error"):
            raise RuntimeError(str(result.get("result") or result.get("subtype")))
        actions = []
        if actions_file.exists():
            for line in actions_file.read_text(encoding="utf-8").splitlines():
                try:
                    actions.append(json.loads(line))
                except ValueError:
                    continue
        return str(result.get("result") or "").strip(), actions


Claude = Callable[[User, str, str, dict], tuple[str, list[dict]]]


def system_prompt(user: User, lang: str, local: datetime) -> str:
    return (
        f"You are the assistant inside the personal work panel of {user.name or user.username} (username {user.username}). "
        f"Now: {local:%A %Y-%m-%d %H:%M} ({local.tzinfo}). Their panel language: {lang}.\n"
        "Do what they ask with the panel tools: add calendar events, expenses, income, tasks, alarms, study deadlines, "
        "clients, client projects and notes; look up their calendar, money, tasks and clients.\n"
        "Rules:\n"
        "- Look up ids with the list tools; never invent ids. Dates are YYYY-MM-DD, times HH:MM, in their time zone.\n"
        "- Changing or deleting existing entries: only with propose_change; it waits for their confirmation, do not claim it is done.\n"
        "- If something important is missing (amount, date, which client), ask one short question instead of guessing.\n"
        "- Answer in the language of their message, short, plain text (it is shown in Telegram): no tables, no markdown headings.\n"
        "- After adding something, say in one line what you added."
    )


async def _history(db: AsyncSession, user_id: int, before_id: int) -> str:
    since = utcnow() - HISTORY
    rows = (await db.scalars(
        select(AssistantMessage).where(AssistantMessage.user_id == user_id, AssistantMessage.at >= since, AssistantMessage.id < before_id)
        .order_by(AssistantMessage.id.desc()).limit(HISTORY_MAX)
    )).all()
    return "\n".join(f"{'User' if m.role == 'user' else 'Assistant'}: {m.text}" for m in reversed(rows))


# ===== Main entry =====
_locks: dict[int, asyncio.Lock] = {}


def out(m: AssistantMessage) -> dict:
    try:
        actions = json.loads(m.actions or "[]")
    except ValueError:
        actions = []
    return {"id": m.id, "at": m.at, "role": m.role, "via": m.via, "engine": m.engine, "text": m.text, "actions": actions}


async def handle(
    db: AsyncSession, user: User, text: str, via: str,
    caller: Caller = api_call, parser: Parser = run_parser, claude: Claude = run_claude,
) -> AssistantMessage:
    """Stores the message, answers it (parser, else Claude) and returns the stored answer."""
    prefs = await prefs_of(db, user.id)
    lang, local = lang_of(prefs), datetime.now(tz_of(prefs))
    t = TEXT[lang]
    asked = AssistantMessage(user_id=user.id, role="user", via=via, text=text.strip()[:4000])
    db.add(asked)
    await db.commit()

    # One answer at a time per user; later messages wait their turn (in order)
    async with _locks.setdefault(user.id, asyncio.Lock()):
        reply = await _answer(db, user, asked, t, lang, local, caller, parser, claude)
    answer = AssistantMessage(user_id=user.id, role="assistant", via=via, engine=reply.engine, text=reply.text, actions=json.dumps(reply.actions, ensure_ascii=False))
    db.add(answer)
    await db.commit()
    return answer


async def _answer(db, user, asked, t, lang, local, caller, parser, claude) -> Reply:
    today = local.date().isoformat()
    parsed = await asyncio.to_thread(parser, asked.text, await parser_ctx(db, user, await prefs_of(db, user.id), local.date()))
    sure, ready = confident(parsed), claude_ready(user)
    if not sure and not ready:
        return Reply(t["noClaude"])
    token = await issue_token(db, user.id)
    if sure:
        code, _, undo = await save_parsed(parsed, today, token, caller)
        if code == 201:
            line = summary(parsed, t, today)
            return Reply(f"✅ {line}", "parser", [{"label": "undo", "kind": "undo", "method": "DELETE", "path": undo, "done": False}] if undo else [])
        if code == 404 and parsed["kind"] == "task":
            return Reply(t["noBoard"], "parser")
        # The API refused it (e.g. a category): Claude may sort it out
        log.info("parser result refused (%s)", code)
        if not ready:
            return Reply(f"{t['failed']} ({code})", "parser")
    history = await _history(db, user.id, asked.id)
    prompt = (f"Earlier in this conversation:\n{history}\n\n" if history else "") + f"Message: {asked.text}"
    tool_env = {"PANEL_API": settings.internal_api_url, "PANEL_COOKIE": settings.cookie_name, "PANEL_TOKEN": token, "PANEL_TODAY": today}
    try:
        text, actions = await asyncio.to_thread(claude, user, prompt, system_prompt(user, lang, local), tool_env)
    except Exception:  # noqa: BLE001 - CLI missing, timeout, limits
        log.exception("claude")
        return Reply(t["claudeFailed"], "claude")
    return Reply(text or t["applied"], "claude", [{**a, "done": False} for a in actions])


async def run_action(db: AsyncSession, user: User, message_id: int, index: int, accept: bool, caller: Caller = api_call) -> tuple[AssistantMessage | None, str]:
    """Undo a created entry or apply / decline a proposed change. Returns (message, result text)."""
    t = TEXT[lang_of(await prefs_of(db, user.id))]
    m = await db.get(AssistantMessage, message_id)
    if m is None or m.user_id != user.id:
        return None, t["gone"]
    actions = json.loads(m.actions or "[]")
    if not 0 <= index < len(actions) or actions[index].get("done"):
        return m, t["gone"]
    a = actions[index]
    if not accept:
        a["done"], result = "declined", t["declined"]
    else:
        token = await issue_token(db, user.id)
        code, _ = await asyncio.to_thread(caller, token, a["method"], a["path"], a.get("body"))
        if code >= 400 or code == 0:
            return m, f"{t['failed']} ({code})"
        a["done"], result = True, t["undone"] if a["kind"] == "undo" else t["applied"]
    m.actions = json.dumps(actions, ensure_ascii=False)
    await db.commit()
    return m, result
