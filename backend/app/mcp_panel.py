"""MCP server (JSON-RPC 2.0) with the panel tools for the assistant's Claude CLI.

Over stdio it is started by assistant.run_claude for one answer: PANEL_API + PANEL_COOKIE + PANEL_TOKEN
(short-lived session of the user who wrote), PANEL_ACTIONS (file where created entries and proposed changes
are recorded for the Undo / Yes buttons), PANEL_TODAY. The sandbox container reaches the same tools over HTTP
(routers/assistant.py), with the same values set per run in RUN. Standard library only; every tool is a
request to the panel API, so the API's own permission rules apply. Changes to existing entries are never
made here: they are only proposed and the user confirms them.
"""

import contextvars
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from typing import Any

PROTOCOL = "2025-06-18"
DATE = {"type": "string", "description": "YYYY-MM-DD"}
TIME = {"type": "string", "description": "HH:MM (24 h)"}
CURRENCY = {"type": "string", "enum": ["EUR", "UAH", "USD"]}
# Entries that may be changed or deleted after the user's confirmation
CHANGEABLE = re.compile(r"^/(expenses|income|events|alarms|cards|clients|projects|client-log|study/works)/\d+$")


# One run over HTTP: {"PANEL_API", "PANEL_COOKIE", "PANEL_TOKEN", "PANEL_TODAY", "actions": list}; stdio uses the environment
RUN: contextvars.ContextVar[dict | None] = contextvars.ContextVar("panel_run", default=None)


def conf(key: str) -> str | None:
    run = RUN.get()
    return run.get(key) if run is not None else os.environ.get(key)


# ===== HTTP to the panel API =====
def api(method: str, path: str, body: dict | None = None, query: dict | None = None) -> Any:
    url = f"{(conf('PANEL_API') or '').rstrip('/')}/api/team{path}"
    if query:
        url += "?" + urllib.parse.urlencode({k: v for k, v in query.items() if v is not None})
    req = urllib.request.Request(
        url, method=method, data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", "Cookie": f"{conf('PANEL_COOKIE') or 'duo_session'}={conf('PANEL_TOKEN') or ''}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise ToolError(f"panel API {e.code}: {detail}") from None
    except OSError as e:  # API not reachable, timeout
        raise ToolError(f"panel API not reachable: {e}") from None


class ToolError(Exception):
    pass


def record(action: dict) -> None:
    run = RUN.get()
    if run is not None:
        run["actions"].append(action)
        return
    path = os.environ.get("PANEL_ACTIONS")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(action, ensure_ascii=False) + "\n")


def created(row: dict, undo: str, label: str) -> dict:
    record({"label": label[:80], "kind": "undo", "method": "DELETE", "path": f"{undo}/{row['id']}"})
    return row


def pick(d: dict, *keys: str) -> dict:
    return {k: d[k] for k in keys if d.get(k) is not None}


def today() -> date:
    return date.fromisoformat(conf("PANEL_TODAY") or date.today().isoformat())


# ===== Tools =====
def add_expense(a: dict, path: str = "/expenses") -> dict:
    body = {"amount": a["amount"], "currency": a.get("currency") or "EUR", "category": a.get("category") or "other",
            "note": a.get("note") or "", "spent_on": a.get("date") or today().isoformat(), **pick(a, "client_id", "project_id")}
    return created(api("POST", path, body), path, f"{a['amount']} {body['currency']} {body['note']}")


def add_income(a: dict) -> dict:
    return add_expense({**a, "category": a.get("category") or "other"}, "/income")


def add_event(a: dict) -> dict:
    start = a.get("start") or "09:00"
    h, m = map(int, start.split(":"))
    end_min = min(h * 60 + m + 60, 23 * 60 + 59)  # one hour, not past midnight
    end = a.get("end") or f"{end_min // 60:02d}:{end_min % 60:02d}"
    body = {"title": a["title"], "date": a["date"], "start": start, "end": end, "note": a.get("note") or "", **pick(a, "client_id", "remind")}
    return created(api("POST", "/events", body), "/events", a["title"])


def add_task(a: dict) -> dict:
    boards = api("GET", "/boards") or []
    board = next((b for b in boards if b["id"] == a.get("board_id")), boards[0] if boards else None)
    if not board or not board.get("columns"):
        raise ToolError("no board with columns; ask the user to create a board first")
    body = {"title": a["title"], **pick(a, "description", "due_date", "assignee_id", "client_id", "project_id")}
    return created(api("POST", f"/columns/{board['columns'][0]['id']}/cards", body), "/cards", a["title"])


def add_alarm(a: dict) -> dict:
    body = {"time": a["time"], "label": a.get("label") or "", "days": a.get("days") or [], "enabled": True}
    return created(api("POST", "/alarms", body), "/alarms", f"{a['time']} {body['label']}")


def add_study_deadline(a: dict) -> dict:
    body = {"title": a["title"], "due": a["due"], "kind": a.get("kind") or "assignment", **pick(a, "due_time", "subject_id")}
    return created(api("POST", "/study/works", body), "/study/works", a["title"])


def add_client(a: dict) -> dict:
    body = pick(a, "name", "company", "email", "phone", "telegram", "website", "tags", "note", "status", "rate", "currency")
    return created(api("POST", "/clients", body), "/clients", a["name"])


def add_client_project(a: dict) -> dict:
    body = pick(a, "title", "budget", "rate", "start", "end")
    return created(api("POST", f"/clients/{a['client_id']}/projects", body), "/projects", a["title"])


def add_client_note(a: dict) -> dict:
    body = {"kind": a.get("kind") or "message", "day": a.get("day") or today().isoformat(), "text": a["text"], **pick(a, "followup")}
    return created(api("POST", f"/clients/{a['client_id']}/log", body), "/client-log", a["text"][:40])


def _occurs(e: dict, day: date) -> bool:
    start = date.fromisoformat(e["date"])
    if e.get("repeat") != "weekly":
        return start == day
    until = date.fromisoformat(e["until"]) if e.get("until") else None
    return day >= start and (until is None or day <= until) and (day.weekday() + 1) % 7 in (e.get("days") or []) and day.isoformat() not in (e.get("skip") or [])


def list_events(a: dict) -> list:
    first = date.fromisoformat(a.get("from") or today().isoformat())
    last = date.fromisoformat(a.get("to") or first.isoformat())
    if (last - first).days > 62:
        raise ToolError("at most 62 days at once")
    events = api("GET", "/events") or []
    out = []
    day = first
    while day <= last:
        out += [{"id": e["id"], "date": day.isoformat(), "start": e["start"], "end": e["end"], "title": e["title"], "client_id": e.get("client_id"),
                 "weekly": e.get("repeat") == "weekly"} for e in events if _occurs(e, day)]
        day += timedelta(days=1)
    return sorted(out, key=lambda x: (x["date"], x["start"]))


def list_money(a: dict) -> dict:
    path = "/income" if a.get("kind") == "income" else "/expenses"
    month = a.get("month") or today().strftime("%Y-%m")
    rows = api("GET", path, query={"month": month}) or []
    totals: dict[str, float] = {}
    for r in rows:
        totals[r["currency"]] = round(totals.get(r["currency"], 0) + float(r["amount"]), 2)
    items = [pick(r, "id", "spent_on", "amount", "currency", "category", "note", "client_id") for r in rows[:100]]
    return {"month": month, "totals": totals, "count": len(rows), "items": items}


def today_overview(_: dict) -> Any:
    return api("GET", "/today")


def list_boards(_: dict) -> list:
    return [{"id": b["id"], "title": b.get("title"), "columns": [{"id": c["id"], "title": c.get("title")} for c in b.get("columns") or []]}
            for b in api("GET", "/boards") or []]


def list_tasks(a: dict) -> list:
    boards = api("GET", "/boards") or []
    ids = [a["board_id"]] if a.get("board_id") else [b["id"] for b in boards]
    out = []
    for bid in ids[:10]:
        full = api("GET", f"/boards/{bid}") or {}
        for col in full.get("columns") or []:
            for c in col.get("cards") or []:
                out.append({"id": c["id"], "board": full.get("title"), "column": col.get("title"), "title": c.get("title"),
                            **pick(c, "due_date", "assignee_id", "client_id", "project_id")})
    return out[:300]


def list_clients(a: dict) -> list:
    q = (a.get("search") or "").lower()
    rows = api("GET", "/clients") or []
    return [pick(c, "id", "name", "company", "status", "tags", "email", "phone") for c in rows
            if not q or q in f"{c.get('name', '')} {c.get('company', '')} {' '.join(c.get('tags') or [])}".lower()][:100]


def get_client(a: dict) -> Any:
    return api("GET", f"/clients/{a['client_id']}")


def list_users(_: dict) -> list:
    return [pick(u, "id", "username", "name") for u in api("GET", "/users") or []]


def propose_change(a: dict) -> str:
    method, path = a["method"].upper(), a["path"]
    if method not in ("PATCH", "DELETE") or not CHANGEABLE.match(path):
        raise ToolError("only PATCH or DELETE of /expenses, /income, /events, /alarms, /cards, /clients, /projects, /client-log, /study/works/<id>")
    record({"label": a["label"][:80], "kind": "confirm", "method": method, "path": path, **({"body": a["body"]} if method == "PATCH" and a.get("body") else {})})
    return "Proposed. The user sees a Yes / No button; it is NOT done until they press Yes. Tell them what you proposed."


def obj(props: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


TOOLS = {
    "add_expense": (add_expense, "Add an expense. Category: food, transport, home, software, tech, fun, health, other.",
                    obj({"amount": {"type": "number"}, "currency": CURRENCY, "category": {"type": "string"}, "note": {"type": "string"}, "date": DATE,
                         "client_id": {"type": "integer"}, "project_id": {"type": "integer"}}, ["amount"])),
    "add_income": (add_income, "Add income. Category: projects, salary, support, sale, gift, refund, other.",
                   obj({"amount": {"type": "number"}, "currency": CURRENCY, "category": {"type": "string"}, "note": {"type": "string"}, "date": DATE,
                        "client_id": {"type": "integer"}, "project_id": {"type": "integer"}}, ["amount"])),
    "add_event": (add_event, "Add a calendar event (default 1 hour). remind = minutes before.",
                  obj({"title": {"type": "string"}, "date": DATE, "start": TIME, "end": TIME, "note": {"type": "string"}, "client_id": {"type": "integer"},
                       "remind": {"type": "integer"}}, ["title", "date"])),
    "add_task": (add_task, "Add a kanban task to the first column of a board (default: first board).",
                 obj({"title": {"type": "string"}, "description": {"type": "string"}, "due_date": DATE, "assignee_id": {"type": "integer"},
                      "client_id": {"type": "integer"}, "project_id": {"type": "integer"}, "board_id": {"type": "integer"}}, ["title"])),
    "add_alarm": (add_alarm, "Add an alarm. days: weekdays to repeat (0 = Sunday … 6 = Saturday), empty = once.",
                  obj({"time": TIME, "label": {"type": "string"}, "days": {"type": "array", "items": {"type": "integer"}}}, ["time"])),
    "add_study_deadline": (add_study_deadline, "Add a study deadline. kind: assignment, project, exam, credit.",
                           obj({"title": {"type": "string"}, "due": DATE, "due_time": TIME, "kind": {"type": "string"}, "subject_id": {"type": "integer"}}, ["title", "due"])),
    "add_client": (add_client, "Add a client to the CRM. status: lead, active, paused, former. tags: short words.",
                   obj({"name": {"type": "string"}, "company": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"},
                        "telegram": {"type": "string"}, "website": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}},
                        "note": {"type": "string"}, "status": {"type": "string"}, "rate": {"type": "number"}, "currency": CURRENCY}, ["name"])),
    "add_client_project": (add_client_project, "Add a project to a client.",
                           obj({"client_id": {"type": "integer"}, "title": {"type": "string"}, "budget": {"type": "number"}, "rate": {"type": "number"},
                                "start": DATE, "end": DATE}, ["client_id", "title"])),
    "add_client_note": (add_client_note, "Add an entry to a client's contact history. kind: call, email, meeting, message. followup = date to get in touch again.",
                        obj({"client_id": {"type": "integer"}, "text": {"type": "string"}, "kind": {"type": "string"}, "day": DATE, "followup": DATE}, ["client_id", "text"])),
    "list_events": (list_events, "Calendar events between two dates (inclusive, weekly repeats expanded).", obj({"from": DATE, "to": DATE}, [])),
    "list_money": (list_money, "Expenses or income of a month with totals.", obj({"kind": {"type": "string", "enum": ["expenses", "income"]}, "month": {"type": "string", "description": "YYYY-MM"}}, [])),
    "today_overview": (today_overview, "The Today screen: plan, tasks due, money of the day.", obj({}, [])),
    "list_boards": (list_boards, "Kanban boards with their columns.", obj({}, [])),
    "list_tasks": (list_tasks, "Tasks (cards) of one board or of all boards.", obj({"board_id": {"type": "integer"}}, [])),
    "list_clients": (list_clients, "Clients, optionally filtered by name, company or tag.", obj({"search": {"type": "string"}}, [])),
    "get_client": (get_client, "One client with projects, contact history, invoices, tasks and meetings.", obj({"client_id": {"type": "integer"}}, ["client_id"])),
    "list_users": (list_users, "Panel users (for assigning tasks).", obj({}, [])),
    "propose_change": (propose_change, "Propose changing (PATCH with body) or deleting (DELETE) an existing entry, e.g. path /events/12. The user must confirm.",
                       obj({"method": {"type": "string", "enum": ["PATCH", "DELETE"]}, "path": {"type": "string"}, "body": {"type": "object"},
                            "label": {"type": "string", "description": "What changes, for the confirm button"}}, ["method", "path", "label"])),
}


# ===== JSON-RPC over stdio =====
def handle(msg: dict) -> dict | None:
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:
        return None  # notification
    if method == "initialize":
        result = {"protocolVersion": (msg.get("params") or {}).get("protocolVersion") or PROTOCOL,
                  "capabilities": {"tools": {}}, "serverInfo": {"name": "panel", "version": "1.0"}}
    elif method == "tools/list":
        result = {"tools": [{"name": n, "description": d, "inputSchema": s} for n, (_, d, s) in TOOLS.items()]}
    elif method == "tools/call":
        params = msg.get("params") or {}
        tool = TOOLS.get(params.get("name"))
        if tool is None:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"unknown tool {params.get('name')}"}}
        try:
            data = tool[0](params.get("arguments") or {})
            result = {"content": [{"type": "text", "text": data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, default=str)}]}
        except (ToolError, KeyError, ValueError, TypeError) as e:
            result = {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
        except Exception as e:  # noqa: BLE001 - one bad call must not stop the server
            result = {"content": [{"type": "text", "text": f"Error: {type(e).__name__}: {e}"}], "isError": True}
    elif method == "ping":
        result = {}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"unknown method {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            reply = handle(json.loads(line))
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        if reply is not None:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
