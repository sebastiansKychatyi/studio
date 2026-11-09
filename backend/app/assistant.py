"""Assistant and chats: one message (panel page or Telegram) → an answer, often an action in the panel.

Each user has one assistant chat and any number of regular chats.
- Assistant: our quick parser (app/utils/quickParse.ts, run by Node) goes first: no AI, instant, free.
  What it does not understand goes to the Claude Code CLI, without memory between answers.
- Regular chat: always Claude, with the model chosen for the chat; the CLI session is resumed, so Claude
  remembers the whole conversation. With ASSISTANT_SANDBOX=docker it also gets a shell and files, but only
  inside the user's own container (workspace /home/claude/work), never on this server.
Claude runs with the user's own Claude: a token they connected themselves in Settings (`claude setup-token`
or an API key, sealed in claude_logins) or a login made on the server (<ASSISTANT_CLAUDE_HOME>/<username>);
nobody uses someone else's subscription. It gets only our panel tools (mcp_panel.py): every action goes
through this API as that user (short-lived session token), so the panel's own rules decide what they may
see and change. Created entries get an "Undo"; changes need a "Yes" first.
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
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import AssistantChat, AssistantMessage, ClaudeLogin, Client, Session, Subject, User
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
MODELS = ("haiku", "sonnet", "opus")  # Claude CLI model aliases
CODE_TOOLS = "Bash,Read,Edit,Write,Glob,Grep,WebFetch,WebSearch"  # only inside the sandbox container
WORKDIR = "/home/claude/work"  # workspace inside the container (kept between chats)

TEXT = {
    "sk": {
        "chatNoClaude": "Bežný chat potrebuje Claude — pripojíš si ho v Nastaveniach → Claude.", "untitled": "Nový chat",
        "expense": "Výdavok", "income": "Príjem", "event": "Udalosť", "task": "Úloha", "alarm": "Budík", "work": "Termín",
        "today": "dnes", "noClaude": "Nerozumiem. Napíš to inak (napr. „káva 3,5 €“ alebo „zajtra 14:00 hovor s Annou“) — Claude si pripojíš v Nastaveniach → Claude.",
        "claudeFailed": "Claude teraz neodpovedá, skús to o chvíľu.", "noBoard": "Najprv vytvor nástenku pre úlohy.",
        "failed": "Nepodarilo sa uložiť", "undone": "Vrátené", "applied": "Hotovo", "declined": "Zrušené", "gone": "Táto akcia už neplatí",
    },
    "cs": {
        "chatNoClaude": "Běžný chat potřebuje Claude — připojíš si ho v Nastavení → Claude.", "untitled": "Nový chat",
        "expense": "Výdaj", "income": "Příjem", "event": "Událost", "task": "Úkol", "alarm": "Budík", "work": "Termín",
        "today": "dnes", "noClaude": "Nerozumím. Napiš to jinak (např. „káva 3,5 €“ nebo „zítra 14:00 hovor s Annou“) — Claude si připojíš v Nastavení → Claude.",
        "claudeFailed": "Claude teď neodpovídá, zkus to za chvíli.", "noBoard": "Nejdřív vytvoř nástěnku pro úkoly.",
        "failed": "Nepodařilo se uložit", "undone": "Vráceno", "applied": "Hotovo", "declined": "Zrušeno", "gone": "Tato akce už neplatí",
    },
    "uk": {
        "chatNoClaude": "Звичайному чату потрібен Claude — підключи його в Налаштуваннях → Claude.", "untitled": "Новий чат",
        "expense": "Витрата", "income": "Дохід", "event": "Подія", "task": "Завдання", "alarm": "Будильник", "work": "Дедлайн",
        "today": "сьогодні", "noClaude": "Не зрозумів. Напиши інакше (напр. «кава 3,5 €» або «завтра 14:00 дзвінок з Анною») — Claude можна підключити в Налаштуваннях → Claude.",
        "claudeFailed": "Claude зараз не відповідає, спробуй трохи пізніше.", "noBoard": "Спершу створи дошку для завдань.",
        "failed": "Не вдалося зберегти", "undone": "Скасовано", "applied": "Готово", "declined": "Відхилено", "gone": "Ця дія вже недійсна",
    },
    "en": {
        "chatNoClaude": "A regular chat needs Claude — connect it in Settings → Claude.", "untitled": "New chat",
        "expense": "Expense", "income": "Income", "event": "Event", "task": "Task", "alarm": "Alarm", "work": "Deadline",
        "today": "today", "noClaude": "I did not get that. Try e.g. “coffee 3.5 €” or “tomorrow 14:00 call with Anna” — connect Claude in Settings → Claude.",
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
async def issue_token(db: AsyncSession, user_id: int, minutes: int = TOKEN_MINUTES) -> str:
    """Short-lived session for one assistant run (same cookie the panel uses)."""
    token = secrets.token_urlsafe(32)
    await db.execute(delete(Session).where(Session.expires_at < utcnow()))
    db.add(Session(token_hash=hashlib.sha256(token.encode()).hexdigest(), user_id=user_id, expires_at=utcnow() + timedelta(minutes=minutes)))
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


def sandbox() -> bool:
    return settings.assistant_sandbox == "docker"


def container(user: User) -> str:
    return f"{settings.assistant_sandbox_prefix}{user.username.lower()}"


def token_kind(token: str) -> str | None:
    """oauth = `claude setup-token` (uses the Claude subscription), api = Anthropic API key (billed per use)."""
    if token.startswith("sk-ant-oat"):
        return "oauth"
    if token.startswith("sk-ant-"):
        return "api"
    return None


def auth_env(kind: str, token: str) -> dict[str, str]:
    return {"CLAUDE_CODE_OAUTH_TOKEN": token} if kind == "oauth" else {"ANTHROPIC_API_KEY": token}


async def claude_login(db: AsyncSession, user: User) -> dict[str, str] | None:
    """How the CLI signs in for this user: own token from Settings first, else a login made on the server."""
    from .monitoring import unseal  # monitoring → telegram → assistant: imported here

    own = await db.get(ClaudeLogin, user.id)
    if own is not None and (token := unseal(own.secret)):
        return auth_env(own.kind, token)
    home = claude_home(user)
    return {"CLAUDE_CONFIG_DIR": str(home)} if home else None


def cli_available() -> bool:
    return bool(settings.assistant_claude and shutil.which(settings.assistant_claude))


def claude_ready(user: User, login: dict[str, str] | None) -> bool:
    if sandbox():  # the CLI lives in the user's container: own token passed in, or a login made there
        return bool(shutil.which("docker") and claude_home(user))
    return bool(login) and cli_available()


@dataclass
class Run:
    """How one Claude answer is run."""

    model: str
    code: bool = False  # shell and files (only in the sandbox container)
    session: str = ""  # CLI session to resume
    keep: bool = False  # keep the session for the next answer (regular chats)
    timeout: int = 120


def claude_args(mcp_config: str, system: str, run: Run | None = None, cli: str | None = None) -> list[str]:
    """Only our MCP server (plus shell and files inside the sandbox); anything else is refused without asking."""
    run = run or Run(settings.assistant_model)
    tools = CODE_TOOLS if run.code else ""
    args = [
        cli or shutil.which(settings.assistant_claude) or settings.assistant_claude, "-p", "--output-format", "json", "--model", run.model,
        "--tools", tools, "--strict-mcp-config", "--mcp-config", mcp_config, "--allowedTools", ",".join(["mcp__panel", *filter(None, tools.split(","))]),
        "--permission-mode", "dontAsk", "--system-prompt", system,
    ]
    if run.session:
        args += ["--resume", run.session]
    if not run.keep:
        args.append("--no-session-persistence")
    return args


def _child_env(home: Path, login: dict[str, str] | None = None) -> dict[str, str]:
    # Only what the CLI needs: no database URL or other secrets of this API
    keep = ("PATH", "HOME", "USERPROFILE", "SYSTEMROOT", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "LANG", "LC_ALL")
    return {**{k: os.environ[k] for k in keep if k in os.environ}, "CLAUDE_CONFIG_DIR": str(home), **(login or {})}


def _result(out: subprocess.CompletedProcess) -> tuple[str, str]:
    """CLI JSON output → (answer text, session id). Raises on failure."""
    try:
        result = json.loads(out.stdout)
    except ValueError:
        raise RuntimeError(f"claude exit {out.returncode}: {out.stderr[-300:]}") from None
    if result.get("is_error"):
        raise RuntimeError(str(result.get("result") or result.get("subtype")))
    return str(result.get("result") or "").strip(), str(result.get("session_id") or "")


def _config_dir(work: str, login: dict[str, str], keep_for: User | None = None) -> Path:
    """Server login: its own folder. Own token: a fresh empty folder per answer (nothing kept on disk),
    or for a regular chat a private folder per user that keeps only the chat sessions (the token stays in the env)."""
    if "CLAUDE_CONFIG_DIR" in login:
        return Path(login["CLAUDE_CONFIG_DIR"])
    if keep_for is not None:
        path = Path(tempfile.gettempdir()) / "duo-assistant" / keep_for.username.lower()
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        return path
    path = Path(work) / "config"
    path.mkdir()
    return path


def _auth_only(login: dict[str, str] | None) -> dict[str, str]:
    return {k: v for k, v in (login or {}).items() if k != "CLAUDE_CONFIG_DIR"}


def check_claude(kind: str, token: str) -> str:
    """Blocking: a tiny call with a new token before it is saved. Returns "" if it works, else the reason."""
    with tempfile.TemporaryDirectory(prefix="assistant-check-") as work:
        run_dir = Path(work) / "cwd"
        run_dir.mkdir()
        try:
            out = subprocess.run(
                [shutil.which(settings.assistant_claude) or settings.assistant_claude, "-p", "--output-format", "json", "--model", settings.assistant_model,
                 "--tools", "", "--strict-mcp-config", "--no-session-persistence"],
                input="Reply with: OK", capture_output=True, text=True, encoding="utf-8", timeout=90, cwd=run_dir,
                env=_child_env(_config_dir(work, {}), auth_env(kind, token)),
            )
        except (OSError, subprocess.TimeoutExpired) as e:
            return f"Claude CLI: {e.__class__.__name__}"
        try:
            result = json.loads(out.stdout)
        except ValueError:
            return (out.stderr or out.stdout or f"exit {out.returncode}").strip()[-300:]
        return str(result.get("result") or result.get("subtype") or "error")[:300] if result.get("is_error") else ""


# Sandbox runs in progress: key in the MCP URL → tool settings and recorded actions (see routers/assistant.py)
SANDBOX_RUNS: dict[str, dict] = {}


def run_claude(
    user: User, prompt: str, system: str, tool_env: dict[str, str], run: Run | None = None, login: dict[str, str] | None = None,
) -> tuple[str, list[dict], str]:
    """Blocking: one Claude answer. Returns (text, actions the tools recorded, session id). Raises on failure."""
    run = run or Run(settings.assistant_model, timeout=settings.assistant_timeout)
    if sandbox():
        if claude_home(user) is None:
            raise RuntimeError("no sandbox for this user")
        return _run_in_container(user, prompt, system, tool_env, run, login)
    if not login:
        raise RuntimeError("no Claude login for this user")
    with tempfile.TemporaryDirectory(prefix="assistant-") as work:
        home = _config_dir(work, login, user if run.keep else None)
        actions_file = Path(work) / "actions.jsonl"
        mcp = Path(work) / "mcp.json"
        mcp.write_text(json.dumps({"mcpServers": {"panel": {
            "command": sys.executable, "args": ["-m", "app.mcp_panel"],
            "env": {**tool_env, "PANEL_ACTIONS": str(actions_file), "PYTHONPATH": str(BACKEND), "PYTHONIOENCODING": "utf-8"},
        }}}), encoding="utf-8")
        # Empty folder: no project files or settings. Kept chats need the same one, the CLI finds sessions by folder.
        run_dir = home / "chats" if run.keep else Path(work) / "cwd"
        run_dir.mkdir(exist_ok=True)
        out = subprocess.run(
            claude_args(str(mcp), system, run), input=prompt, capture_output=True, text=True, encoding="utf-8",
            timeout=run.timeout, cwd=run_dir, env=_child_env(home, _auth_only(login)),
        )
        text, session = _result(out)
        actions = []
        if actions_file.exists():
            for line in actions_file.read_text(encoding="utf-8").splitlines():
                try:
                    actions.append(json.loads(line))
                except ValueError:
                    continue
        return text, actions, session


def _run_in_container(user: User, prompt: str, system: str, tool_env: dict[str, str], run: Run, login: dict[str, str] | None = None) -> tuple[str, list[dict], str]:
    """Claude inside the user's container; the panel tools are reached over HTTP with a one-run key.
    An own token from Settings is passed by name (-e), so it is not on the command line."""
    key = secrets.token_urlsafe(24)
    SANDBOX_RUNS[key] = {**tool_env, "actions": []}
    base = (settings.assistant_sandbox_api or settings.site_url).rstrip("/")
    mcp = json.dumps({"mcpServers": {"panel": {"type": "http", "url": f"{base}/api/team/assistant/mcp/{key}"}}})
    auth = _auth_only(login)
    cmd = ["docker", "exec", "-i", "-w", WORKDIR, *[a for k in auth for a in ("-e", k)], container(user), *claude_args(mcp, system, run, cli="claude")]
    env = {**{k: os.environ[k] for k in ("PATH", "HOME", "DOCKER_HOST", "DOCKER_CONFIG", "SYSTEMROOT") if k in os.environ}, **auth}
    try:
        out = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=run.timeout, env=env)
        text, session = _result(out)
    finally:
        actions = SANDBOX_RUNS.pop(key)["actions"]
    return text, actions, session


Claude = Callable[..., tuple]  # (user, prompt, system, tool_env, run, login) → (text, actions[, session])


def system_prompt(user: User, lang: str, local: datetime) -> str:
    return (
        f"You are the assistant inside the personal work panel of {user.name or user.username} (username {user.username}). "
        f"Now: {local:%A %Y-%m-%d %H:%M} ({local.tzinfo}). Their panel language: {lang}.\n"
        "Do what they ask with the panel tools: add calendar events, expenses, income, tasks, alarms, study deadlines, "
        "clients, client projects and notes; look up their calendar, money, tasks and clients.\n"
        "Rules:\n" + RULES +
        "- Answer in the language of their message, short, plain text (it is shown in Telegram): no tables, no markdown headings.\n"
        "- After adding something, say in one line what you added."
    )


RULES = (
    "- Look up ids with the list tools; never invent ids. Dates are YYYY-MM-DD, times HH:MM, in their time zone.\n"
    "- Changing or deleting existing entries: only with propose_change; it waits for their confirmation, do not claim it is done.\n"
    "- If something important is missing (amount, date, which client), ask one short question instead of guessing.\n"
)


def chat_prompt(user: User, lang: str, local: datetime, code: bool) -> str:
    """Regular chat: a normal conversation, plus the panel tools (and the workspace in the sandbox)."""
    work = (
        f"You work in the user's own sandbox container. Workspace: {WORKDIR} (kept between chats, one folder per project). "
        "You may write code, run commands, install packages and run tests there. Never print secrets you find. "
        "Before big or destructive steps (deleting many files, publishing, sending anything out) describe the plan and wait for their OK.\n"
        if code else
        "There is no shell and no file access here: if they want code, write it in the answer.\n"
    )
    return (
        f"You are Claude, in a chat inside the work panel of {user.name or user.username} (username {user.username}). "
        f"Now: {local:%A %Y-%m-%d %H:%M} ({local.tzinfo}). Their panel language: {lang}.\n"
        "Talk with them normally. You also have the panel tools (calendar, expenses, income, tasks, alarms, study, clients) "
        "and may use them when they ask.\n" + work + "Rules for the panel tools:\n" + RULES +
        "- Answer in the language of their message. The chat is also shown in Telegram: prefer short paragraphs and lists, "
        "short code blocks are fine, no tables."
    )


async def _history(db: AsyncSession, chat_id: int, before_id: int) -> str:
    since = utcnow() - HISTORY
    rows = (await db.scalars(
        select(AssistantMessage).where(AssistantMessage.chat_id == chat_id, AssistantMessage.at >= since, AssistantMessage.id < before_id)
        .order_by(AssistantMessage.id.desc()).limit(HISTORY_MAX)
    )).all()
    return "\n".join(f"{'User' if m.role == 'user' else 'Assistant'}: {m.text}" for m in reversed(rows))


# ===== Chats =====
async def main_chat(db: AsyncSession, user_id: int) -> AssistantChat:
    """The assistant chat of a user; created on first use, with the messages from before chats existed."""
    chat = (await db.scalars(
        select(AssistantChat).where(AssistantChat.user_id == user_id, AssistantChat.kind == "assistant").order_by(AssistantChat.id)
    )).first()
    if chat is None:
        chat = AssistantChat(user_id=user_id, kind="assistant")
        db.add(chat)
        await db.flush()
        await db.execute(update(AssistantMessage).where(AssistantMessage.user_id == user_id, AssistantMessage.chat_id.is_(None)).values(chat_id=chat.id))
        await db.commit()
    return chat


async def chat_of(db: AsyncSession, user: User, chat_id: int | None) -> AssistantChat | None:
    """Own chat by id (None = the assistant); someone else's chat is None."""
    if chat_id is None:
        return await main_chat(db, user.id)
    chat = await db.get(AssistantChat, chat_id)
    return chat if chat is not None and chat.user_id == user.id else None


async def chats_of(db: AsyncSession, user: User) -> list[AssistantChat]:
    """The assistant first, then regular chats, latest first."""
    main = await main_chat(db, user.id)
    rest = (await db.scalars(
        select(AssistantChat).where(AssistantChat.user_id == user.id, AssistantChat.kind == "chat")
        .order_by(AssistantChat.updated_at.desc(), AssistantChat.id.desc())
    )).all()
    return [main, *rest]


async def new_chat(db: AsyncSession, user: User, title: str = "", model: str = "") -> AssistantChat:
    chat = AssistantChat(user_id=user.id, kind="chat", title=title.strip()[:120], model=model if model in MODELS else "")
    db.add(chat)
    await db.commit()
    return chat


def model_of(chat: AssistantChat) -> str:
    if chat.model in MODELS:
        return chat.model
    return settings.assistant_model if chat.kind == "assistant" else settings.assistant_chat_model


# ===== Main entry =====
_locks: dict[int, asyncio.Lock] = {}  # per chat: answers in order; other chats are not held up
_pending: dict[int, int] = {}  # chat id → questions not answered yet


def busy(chat_id: int) -> bool:
    return _pending.get(chat_id, 0) > 0


def _done(chat_id: int) -> None:
    _pending[chat_id] = max(0, _pending.get(chat_id, 1) - 1)


def out(m: AssistantMessage) -> dict:
    try:
        actions = json.loads(m.actions or "[]")
    except ValueError:
        actions = []
    return {"id": m.id, "at": m.at, "role": m.role, "via": m.via, "engine": m.engine, "text": m.text, "actions": actions}


async def ask(db: AsyncSession, user: User, chat: AssistantChat, text: str, via: str) -> AssistantMessage:
    """Stores a question; answer() must follow (now or in the background)."""
    asked = AssistantMessage(user_id=user.id, chat_id=chat.id, role="user", via=via, text=text.strip()[:4000])
    db.add(asked)
    if chat.kind == "chat" and not chat.title:
        chat.title = " ".join(asked.text.split())[:60]
    chat.updated_at = utcnow()
    await db.commit()
    _pending[chat.id] = _pending.get(chat.id, 0) + 1
    return asked


async def answer(
    db: AsyncSession, user: User, chat: AssistantChat, asked: AssistantMessage,
    caller: Caller = api_call, parser: Parser = run_parser, claude: Claude = run_claude,
) -> AssistantMessage:
    """Answers a stored question and stores the answer."""
    try:
        prefs = await prefs_of(db, user.id)
        lang, local = lang_of(prefs), datetime.now(tz_of(prefs))
        t = TEXT[lang]
        async with _locks.setdefault(chat.id, asyncio.Lock()):
            if chat.kind == "assistant":
                reply = await _answer(db, user, chat, asked, t, lang, local, caller, parser, claude)
            else:
                reply = await _answer_chat(db, user, chat, asked, t, lang, local, claude)
        m = AssistantMessage(user_id=user.id, chat_id=chat.id, role="assistant", via=asked.via, engine=reply.engine, text=reply.text,
                             actions=json.dumps(reply.actions, ensure_ascii=False))
        db.add(m)
        chat.updated_at = utcnow()
        await db.commit()
        return m
    finally:
        _done(chat.id)


async def handle(
    db: AsyncSession, user: User, text: str, via: str,
    caller: Caller = api_call, parser: Parser = run_parser, claude: Claude = run_claude, chat: AssistantChat | None = None,
) -> AssistantMessage:
    """Stores the message, answers it and returns the stored answer (default chat: the assistant)."""
    chat = chat or await main_chat(db, user.id)
    asked = await ask(db, user, chat, text, via)
    return await answer(db, user, chat, asked, caller, parser, claude)


async def answer_later(user_id: int, chat_id: int, asked_id: int, late_after: float | None = None, sessions=None, **fakes) -> dict | None:
    """Background answer for the panel page (the request may end first; the page polls).
    An answer that takes longer than late_after seconds also goes to the user's Telegram, if linked."""
    from . import telegram
    from .db import SessionLocal

    started = time.monotonic()
    async with (sessions or SessionLocal)() as db:
        user, chat, asked = await db.get(User, user_id), await db.get(AssistantChat, chat_id), await db.get(AssistantMessage, asked_id)
        if user is None or chat is None or asked is None:
            _done(chat_id)
            return None
        try:
            m = await answer(db, user, chat, asked, **fakes)
        except Exception:  # noqa: BLE001 - logged; the page stops waiting when the chat is no longer busy
            log.exception("assistant answer")
            return None
        if late_after is not None and time.monotonic() - started > late_after and telegram.configured():
            tg = await telegram.chat_of(db, user.id)
            if tg is not None:
                await telegram.send_answer(db, user, tg, chat, m)
        return out(m)


def _call(claude: Claude, *args) -> tuple[str, list[dict], str]:
    res = claude(*args)
    return res[0], res[1], res[2] if len(res) > 2 else ""


def _tool_env(token: str, today: str) -> dict[str, str]:
    return {"PANEL_API": settings.internal_api_url, "PANEL_COOKIE": settings.cookie_name, "PANEL_TOKEN": token, "PANEL_TODAY": today}


async def _answer(db, user, chat, asked, t, lang, local, caller, parser, claude) -> Reply:
    today = local.date().isoformat()
    parsed = await asyncio.to_thread(parser, asked.text, await parser_ctx(db, user, await prefs_of(db, user.id), local.date()))
    login = await claude_login(db, user)
    sure, ready = confident(parsed), claude_ready(user, login)
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
    history = await _history(db, chat.id, asked.id)
    prompt = (f"Earlier in this conversation:\n{history}\n\n" if history else "") + f"Message: {asked.text}"
    run = Run(model_of(chat), timeout=settings.assistant_timeout)
    try:
        text, actions, _ = await asyncio.to_thread(_call, claude, user, prompt, system_prompt(user, lang, local), _tool_env(token, today), run, login)
    except Exception:  # noqa: BLE001 - CLI missing, timeout, limits
        log.exception("claude")
        return Reply(t["claudeFailed"], "claude")
    return Reply(text or t["applied"], "claude", [{**a, "done": False} for a in actions])


async def _answer_chat(db, user, chat, asked, t, lang, local, claude) -> Reply:
    """Regular chat: Claude only; the CLI session keeps the conversation."""
    login = await claude_login(db, user)
    if not claude_ready(user, login):
        return Reply(t["chatNoClaude"])
    token = await issue_token(db, user.id, settings.assistant_chat_timeout // 60 + 5)
    system = chat_prompt(user, lang, local, sandbox())
    env = _tool_env(token, local.date().isoformat())
    run = Run(model_of(chat), code=sandbox(), session=chat.session, keep=True, timeout=settings.assistant_chat_timeout)
    try:
        try:
            text, actions, session = await asyncio.to_thread(_call, claude, user, asked.text, system, env, run, login)
        except Exception:
            if not run.session:
                raise
            # The session may be gone (new login, cleaned up): a new one with the recent messages
            log.warning("claude session %s not resumed, starting a new one", run.session)
            history = await _history(db, chat.id, asked.id)
            prompt = (f"Earlier in this conversation:\n{history}\n\n" if history else "") + asked.text
            run = Run(run.model, code=run.code, keep=True, timeout=run.timeout)
            text, actions, session = await asyncio.to_thread(_call, claude, user, prompt, system, env, run, login)
    except Exception:  # noqa: BLE001 - CLI missing, timeout, limits
        log.exception("claude chat")
        return Reply(t["claudeFailed"], "claude")
    if session:
        chat.session = session
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
