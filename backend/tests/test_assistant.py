"""Assistant, its MCP tools and the Telegram bot. Run from backend/:  python -m unittest discover -s tests -v
The panel API, the Claude CLI and the Telegram Bot API are replaced by fakes; the database is in-memory SQLite (aiosqlite)."""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from datetime import timedelta, timezone
from pathlib import Path
from unittest import mock

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
if importlib.util.find_spec("pywebpush") is None:  # not needed here, only imported by notify
    stub = types.ModuleType("pywebpush")
    stub.WebPushException, stub.webpush = Exception, lambda *a, **k: None
    sys.modules["pywebpush"] = stub

from app import assistant, mcp_panel, notify, telegram  # noqa: E402

TODAY = "2026-11-09"


class Api:
    """Fake panel API: records requests, answers like the real one."""

    def __init__(self, boards=None):
        self.calls, self.next_id, self.boards = [], 100, boards if boards is not None else [{"id": 1, "title": "Studio", "columns": [{"id": 7, "title": "To do"}]}]

    def __call__(self, token, method, path, body=None):
        self.calls.append((method, path, body, token))
        if method == "GET" and path == "/boards":
            return 200, self.boards
        if method == "POST":
            self.next_id += 1
            return 201, {"id": self.next_id, **(body or {})}
        return (204, None) if method == "DELETE" else (200, {})


class DecisionTest(unittest.TestCase):
    def test_confident(self):
        self.assertTrue(assistant.confident({"kind": "expense", "confidence": 0.9, "amount": 5}))
        self.assertFalse(assistant.confident({"kind": "task", "confidence": 0.4, "title": "Add client Anna"}))  # goes to Claude
        self.assertFalse(assistant.confident({"kind": "expense", "confidence": 0.9}))  # no amount
        self.assertFalse(assistant.confident({"kind": "alarm", "confidence": 0.95}))  # no time
        self.assertFalse(assistant.confident(None))

    def test_summary(self):
        t = assistant.TEXT["en"]
        self.assertEqual(assistant.summary({"kind": "expense", "amount": 5, "currency": "EUR", "title": "Cigarettes", "date": TODAY}, t, TODAY), "Expense: 5,00 € · Cigarettes")
        self.assertEqual(assistant.summary({"kind": "event", "title": "Call", "date": "2026-11-10", "time": "14:00", "end": "15:00"}, t, TODAY), "Event: Call · 10.11 14:00–15:00")

    def test_claude_has_no_built_in_tools(self):
        args = assistant.claude_args("mcp.json", "sys")
        self.assertEqual(args[args.index("--tools") + 1], "")
        self.assertEqual(args[args.index("--allowedTools") + 1], "mcp__panel")
        self.assertEqual(args[args.index("--permission-mode") + 1], "dontAsk")
        self.assertIn("--strict-mcp-config", args)
        self.assertFalse(any("dangerously" in a or a == "bypassPermissions" for a in args))

    def test_child_env_has_no_secrets(self):
        with mock.patch.dict(os.environ, {"DATABASE_URL": "postgres://secret", "TELEGRAM_BOT_TOKEN": "x", "PATH": "/bin"}):
            env = assistant._child_env(Path("/srv/claude/seb"))
        self.assertEqual(env["CLAUDE_CONFIG_DIR"], str(Path("/srv/claude/seb")))
        self.assertNotIn("DATABASE_URL", env)
        self.assertNotIn("TELEGRAM_BOT_TOKEN", env)

    def test_claude_home_per_user(self):
        with tempfile.TemporaryDirectory() as home:
            (Path(home) / "seb").mkdir()
            with mock.patch.object(assistant.settings, "assistant_claude_home", home):
                self.assertEqual(assistant.claude_home(types.SimpleNamespace(username="Seb")), Path(home) / "seb")
                self.assertIsNone(assistant.claude_home(types.SimpleNamespace(username="roman")))  # no login: no Claude


class SaveTest(unittest.IsolatedAsyncioTestCase):
    async def test_expense_like_quick_add(self):
        api = Api()
        code, _, undo = await assistant.save_parsed({"kind": "expense", "amount": 5, "currency": "EUR", "category": "other", "title": "Cigarettes"}, TODAY, "tok", api)
        self.assertEqual((code, undo), (201, "/expenses/101"))
        self.assertEqual(api.calls[0][:3], ("POST", "/expenses", {"amount": 5, "currency": "EUR", "category": "other", "note": "Cigarettes", "spent_on": TODAY}))

    async def test_task_goes_to_first_column(self):
        api = Api()
        _, _, undo = await assistant.save_parsed({"kind": "task", "title": "Call Anna", "date": "2026-11-12"}, TODAY, "tok", api)
        self.assertEqual(api.calls[1][1], "/columns/7/cards")
        self.assertEqual(undo, "/cards/101")
        code, _, _ = await assistant.save_parsed({"kind": "task", "title": "x"}, TODAY, "tok", Api(boards=[]))
        self.assertEqual(code, 404)


@unittest.skipUnless(shutil.which("node") and assistant.PARSER.exists(), "needs Node 22+ for the quick parser")
class ParserTest(unittest.TestCase):
    def test_same_parser_as_the_panel(self):
        ctx = {"today": TODAY, "currency": "EUR", "clients": [], "users": [], "subjects": []}
        r = assistant.run_parser("кофе 3,5 €", ctx)
        self.assertEqual((r["kind"], r["amount"], r["currency"]), ("expense", 3.5, "EUR"))
        self.assertTrue(assistant.confident(r))
        self.assertFalse(assistant.confident(assistant.run_parser("добавь клиента Анна барбекю", ctx)))


@unittest.skipUnless(importlib.util.find_spec("aiosqlite"), "needs aiosqlite for the in-memory database")
class DbCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

        from app.models import Base, User

        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.Session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.db = self.Session()
        self.seb, self.roman = User(username="seb", name="Sebastian", password_hash="x"), User(username="roman", name="Roman", password_hash="x")
        self.db.add_all([self.seb, self.roman])
        await self.db.commit()
        # Windows without tzdata (it is in requirements.txt): time zones fall back to UTC
        if importlib.util.find_spec("tzdata") is None and sys.platform == "win32":
            for module in (notify, assistant):
                tz = mock.patch.object(module, "tz_of", return_value=timezone.utc)
                tz.start()
                self.addCleanup(tz.stop)

    async def asyncTearDown(self):
        await self.db.close()
        await self.engine.dispose()


class HandleTest(DbCase):
    async def test_parser_first_claude_not_called(self):
        api = Api()
        claude = mock.Mock()
        parser = lambda text, ctx: {"kind": "expense", "confidence": 0.9, "amount": 5, "currency": "EUR", "category": "other", "title": "Cigarettes", "date": ctx["today"]}  # noqa: E731
        m = await assistant.handle(self.db, self.seb, "Расход 5 евро сижке", "telegram", api, parser, claude)
        claude.assert_not_called()
        self.assertEqual(m.engine, "parser")
        self.assertTrue(m.text.startswith("✅"))
        actions = json.loads(m.actions)
        self.assertEqual((actions[0]["kind"], actions[0]["path"]), ("undo", "/expenses/101"))

    async def test_not_understood_goes_to_claude_of_this_user(self):
        api, seen = Api(), {}

        def claude(user, prompt, system, env):
            seen.update(user=user.username, prompt=prompt, env=env)
            return "Added client Anna (tag: barbecue).", [{"label": "Anna", "kind": "undo", "method": "DELETE", "path": "/clients/5"}]

        parser = lambda text, ctx: {"kind": "task", "confidence": 0.4, "title": text}  # noqa: E731
        with mock.patch.object(assistant, "claude_ready", return_value=True):
            m = await assistant.handle(self.db, self.seb, "добав клиента Анна барбекю", "telegram", api, parser, claude)
        self.assertEqual(api.calls, [])  # nothing saved by the parser
        self.assertEqual((m.engine, m.text), ("claude", "Added client Anna (tag: barbecue)."))
        self.assertEqual(seen["user"], "seb")
        self.assertIn("добав клиента Анна барбекю", seen["prompt"])
        self.assertTrue(seen["env"]["PANEL_TOKEN"])
        self.assertEqual(json.loads(m.actions)[0]["path"], "/clients/5")

    async def test_session_token_is_short_lived_and_works(self):
        from sqlalchemy import select

        from app.models import Session

        token = await assistant.issue_token(self.db, self.seb.id)
        row = (await self.db.scalars(select(Session))).one()
        self.assertEqual(row.user_id, self.seb.id)
        self.assertNotEqual(row.token_hash, token)  # only the hash is stored
        expires = row.expires_at.replace(tzinfo=None) - assistant.utcnow().replace(tzinfo=None)
        self.assertLessEqual(expires, timedelta(minutes=assistant.TOKEN_MINUTES))

    async def test_without_claude_says_how_to_write(self):
        parser = lambda text, ctx: {"kind": None, "confidence": 0}  # noqa: E731
        with mock.patch.object(assistant, "claude_ready", return_value=False):
            m = await assistant.handle(self.db, self.seb, "hmm", "panel", Api(), parser, mock.Mock())
        self.assertIn("Claude", m.text)

    async def test_history_is_per_user(self):
        prompts = []
        parser = lambda text, ctx: None  # noqa: E731

        def claude(user, prompt, system, env):
            prompts.append((user.username, prompt))
            return "ok", []

        with mock.patch.object(assistant, "claude_ready", return_value=True):
            await assistant.handle(self.db, self.roman, "secret of Roman", "panel", Api(), parser, claude)
            await assistant.handle(self.db, self.seb, "first", "panel", Api(), parser, claude)
            await assistant.handle(self.db, self.seb, "second", "panel", Api(), parser, claude)
        self.assertIn("User: first", prompts[2][1])
        self.assertFalse(any("Roman" in p for u, p in prompts if u == "seb"))

    async def test_undo_once_and_only_own(self):
        api = Api()
        parser = lambda text, ctx: {"kind": "alarm", "confidence": 0.95, "time": "06:30", "days": []}  # noqa: E731
        m = await assistant.handle(self.db, self.seb, "budík 6:30", "panel", api, parser, mock.Mock())
        other, _ = await assistant.run_action(self.db, self.roman, m.id, 0, True, api)
        self.assertIsNone(other)  # Roman cannot touch Seb's message
        _, result = await assistant.run_action(self.db, self.seb, m.id, 0, True, api)
        self.assertEqual(api.calls[-1][:2], ("DELETE", "/alarms/101"))
        self.assertTrue(json.loads(m.actions)[0]["done"])
        n = len(api.calls)
        _, again = await assistant.run_action(self.db, self.seb, m.id, 0, True, api)
        self.assertEqual(len(api.calls), n)  # not twice
        self.assertNotEqual(result, again)

    async def test_declined_change_is_not_sent(self):
        from app.models import AssistantMessage

        m = AssistantMessage(user_id=self.seb.id, role="assistant", text="Delete event?", actions=json.dumps([{"label": "Delete Call", "kind": "confirm", "method": "DELETE", "path": "/events/3"}]))
        self.db.add(m)
        await self.db.commit()
        api = Api()
        await assistant.run_action(self.db, self.seb, m.id, 0, False, api)
        self.assertEqual(api.calls, [])
        self.assertEqual(json.loads(m.actions)[0]["done"], "declined")


class McpTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.actions = Path(self.dir.name) / "a.jsonl"
        self.env = mock.patch.dict(os.environ, {"PANEL_API": "http://x", "PANEL_TOKEN": "t", "PANEL_ACTIONS": str(self.actions), "PANEL_TODAY": TODAY})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.dir.cleanup()

    def call(self, name, args):
        return mcp_panel.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}})["result"]

    def test_protocol(self):
        init = mcp_panel.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(init["result"]["serverInfo"]["name"], "panel")
        self.assertIsNone(mcp_panel.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        names = {t["name"] for t in mcp_panel.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]}
        self.assertTrue({"add_expense", "add_event", "add_client", "list_events", "propose_change"} <= names)
        self.assertFalse(any("delete" in n or "update" in n for n in names))  # no direct changes

    def test_created_entries_get_undo(self):
        with mock.patch.object(mcp_panel, "api", return_value={"id": 5, "name": "Anna"}) as api:
            res = self.call("add_client", {"name": "Anna", "tags": ["barbecue"]})
        self.assertNotIn("isError", res)
        api.assert_called_once_with("POST", "/clients", {"name": "Anna", "tags": ["barbecue"]})
        self.assertEqual(json.loads(self.actions.read_text(encoding="utf-8")), {"label": "Anna", "kind": "undo", "method": "DELETE", "path": "/clients/5"})

    def test_changes_are_only_proposed(self):
        with mock.patch.object(mcp_panel, "api") as api:
            ok = self.call("propose_change", {"method": "DELETE", "path": "/events/3", "label": "Delete Call"})
            bad = self.call("propose_change", {"method": "DELETE", "path": "/users/1", "label": "x"})
            post = self.call("propose_change", {"method": "POST", "path": "/events/3", "label": "x"})
        api.assert_not_called()
        self.assertIn("NOT done", ok["content"][0]["text"])
        self.assertTrue(bad["isError"] and post["isError"])
        self.assertEqual(len(self.actions.read_text(encoding="utf-8").splitlines()), 1)

    def test_list_events_expands_weekly(self):
        events = [{"id": 1, "title": "Gym", "date": "2026-11-02", "start": "18:00", "end": "19:00", "repeat": "weekly", "days": [1, 3], "until": None, "skip": ["2026-11-11"]},
                  {"id": 2, "title": "Call", "date": "2026-11-10", "start": "14:00", "end": "15:00", "repeat": "none", "days": [], "until": None, "skip": []}]
        with mock.patch.object(mcp_panel, "api", return_value=events):
            res = json.loads(self.call("list_events", {"from": "2026-11-09", "to": "2026-11-11"})["content"][0]["text"])
        self.assertEqual([(e["date"], e["title"]) for e in res], [("2026-11-09", "Gym"), ("2026-11-10", "Call")])  # Wed 11th skipped


class TelegramTest(DbCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.sent = []
        self.patch = mock.patch.object(telegram.settings, "telegram_bot_token", "123:abc")
        self.patch.start()
        telegram._username = None

    async def asyncTearDown(self):
        self.patch.stop()
        telegram._username = None
        await super().asyncTearDown()

    def api(self, method, params):
        self.sent.append((method, params))
        return {"username": "duo_panel_bot"} if method == "getMe" else {"message_id": 1}

    def texts(self):
        return [p["text"] for m, p in self.sent if m == "sendMessage"]

    def msg(self, chat_id, text, kind="private"):
        return {"update_id": 1, "message": {"chat": {"id": chat_id, "type": kind}, "from": {"id": chat_id, "language_code": "en"}, "text": text}}

    async def link(self, user, chat_id):
        url = await telegram.link_url(self.db, user.id, self.api)
        await telegram.handle_update(self.db, self.msg(chat_id, f"/start {url.split('start=')[1]}"), self.api)

    async def test_link_with_one_time_code(self):
        url = await telegram.link_url(self.db, self.seb.id, self.api)
        self.assertTrue(url.startswith("https://t.me/duo_panel_bot?start="))
        await telegram.handle_update(self.db, self.msg(555, f"/start {url.split('start=')[1]}"), self.api)
        self.assertEqual(await telegram.chat_of(self.db, self.seb.id), 555)
        # The same code does not work twice
        await telegram.handle_update(self.db, self.msg(777, f"/start {url.split('start=')[1]}"), self.api)
        self.assertIsNone(await telegram.chat_of(self.db, self.roman.id))
        self.assertEqual(await telegram.chat_of(self.db, self.seb.id), 555)

    async def test_strangers_and_groups_get_nothing(self):
        with mock.patch.object(assistant, "handle") as handle:
            await telegram.handle_update(self.db, self.msg(999, "кофе 3 €"), self.api)
            await telegram.handle_update(self.db, self.msg(-100, "кофе 3 €", "group"), self.api)
        handle.assert_not_called()
        self.assertEqual(self.texts(), [telegram.TEXT["en"]["notLinked"]])

    async def test_message_goes_to_the_assistant_of_that_user(self):
        await self.link(self.seb, 555)
        await self.link(self.roman, 666)
        self.sent.clear()
        from app.models import AssistantMessage

        async def fake_handle(db, user, text, via):
            m = AssistantMessage(user_id=user.id, role="assistant", text=f"hi {user.username}", actions=json.dumps([{"label": "undo", "kind": "undo", "method": "DELETE", "path": "/expenses/1"}]))
            db.add(m)
            await db.commit()
            return m

        with mock.patch.object(assistant, "handle", side_effect=fake_handle) as handle:
            await telegram.handle_update(self.db, self.msg(666, "кофе 3 €"), self.api)
        self.assertEqual(handle.call_args.args[1].username, "roman")
        reply = [p for m, p in self.sent if m == "sendMessage"][0]
        self.assertEqual((reply["chat_id"], reply["text"]), (666, "hi roman"))
        self.assertTrue(reply["reply_markup"]["inline_keyboard"][0][0]["callback_data"].startswith("a:"))

    async def test_callback_of_another_chat_is_ignored(self):
        from app.models import AssistantMessage

        await self.link(self.seb, 555)
        await self.link(self.roman, 666)
        m = AssistantMessage(user_id=self.seb.id, role="assistant", text="x", actions=json.dumps([{"label": "undo", "kind": "undo", "method": "DELETE", "path": "/expenses/1"}]))
        self.db.add(m)
        await self.db.commit()
        self.sent.clear()
        with mock.patch.object(assistant, "issue_token") as token:
            await telegram.handle_update(self.db, {"update_id": 2, "callback_query": {"id": "q", "data": f"a:{m.id}:0", "message": {"message_id": 9, "chat": {"id": 666}}}}, self.api)
        token.assert_not_called()  # Roman's chat never gets as far as the API
        self.assertFalse(json.loads(m.actions)[0].get("done"))
        self.assertEqual([x for x, _ in self.sent], ["answerCallbackQuery"])

    def test_push_message(self):
        with mock.patch.object(telegram.settings, "site_url", "https://studio.k2drive.com"):
            text, markup = telegram.push_message({"title": "⏰ 06:30", "body": "Gym <3", "url": "/sk/panel/alarms", "alarm": {"id": 4}}, telegram.TEXT["sk"], True)
        self.assertEqual(text, "<b>⏰ 06:30</b>\nGym &lt;3")
        buttons = markup["inline_keyboard"][0]
        self.assertEqual(buttons[0]["callback_data"], "z:4")
        self.assertEqual(buttons[1]["url"], "https://studio.k2drive.com/sk/panel/alarms")

    async def test_notify_respects_settings(self):
        from app.models import UserSettings

        await self.link(self.seb, 555)
        build = lambda t, lang: {"title": "Deadline", "body": "Essay"}  # noqa: E731
        with mock.patch.object(notify, "enabled", return_value=False), mock.patch.object(telegram, "notify", return_value=1) as tg:
            self.assertEqual(await notify.send(self.db, self.seb.id, "study", build), 1)
            self.assertEqual(await notify.send(self.db, self.roman.id, "study", build), 0)  # no chat
            self.db.add(UserSettings(user_id=self.seb.id, data=json.dumps({"notify": {"study": False}})))
            await self.db.commit()
            self.assertEqual(await notify.send(self.db, self.seb.id, "study", build), 0)  # kind switched off
            (await self.db.get(UserSettings, self.seb.id)).data = json.dumps({"notify": {"telegram": False}})
            await self.db.commit()
            self.assertEqual(await notify.send(self.db, self.seb.id, "study", build), 0)  # Telegram switched off
        self.assertEqual(tg.call_count, 1)
        self.assertEqual(tg.call_args.args[0], 555)


if __name__ == "__main__":
    unittest.main()
