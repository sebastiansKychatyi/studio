"""Project monitoring (e-Drivebook contract). Run from backend/:  python -m unittest discover -s tests -v
HTTP to e-Drivebook is replaced by fake fetchers; the database tests use in-memory SQLite (aiosqlite)."""

import hashlib
import hmac
import importlib.util
import json
import os
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import mock

# Settings must not need a real database for the pure tests
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from app import monitoring as mon  # noqa: E402
from app.monitoring import Response  # noqa: E402

T0 = datetime(2026, 11, 5, 8, 0, tzinfo=timezone.utc)
OK = {"status": "ok", "time": "2026-11-05T08:00:00Z", "version": "1.0.0", "checks": {"database": {"ok": True, "detail": "", "latency_ms": 3}}, "errors": {"open": 0, "last_1h": 0}}
DEGRADED = {
    "status": "degraded",
    "time": "2026-11-05T08:00:00Z",
    "checks": {"database": {"ok": True}, "redis": {"ok": False, "detail": "connection refused"}},
    "scheduler": {"running": True, "jobs": [
        {"id": "reminders", "name": "Reminders", "stale": True, "last_status": "ok"},
        {"id": "backup", "name": "Backup", "stale": False, "last_status": "error", "last_error": "disk full"},
        {"id": "fine", "name": "Fine", "stale": False, "last_status": "ok"},
    ]},
    "errors": {"open": 2, "last_1h": 1},
}


def env(**kw):
    """Plain object with the fields of MonitorEnv."""
    base = dict(id=1, project_id=1, name="prod", base_url="https://e-drivebook.com/v1/monitoring/external", api_token="t", webhook_secret="",
                enabled=True, state="unknown", status="", fail_count=0, last_poll_at=None, last_ok_at=None, last_error="", down_since=None,
                degraded_since=None, degraded_alerted=False, token_invalid=False, snapshot="", errors_cursor="", errors_polled_at=None)
    base.update(kw)
    return SimpleNamespace(**base)


def poll(e, res, minutes=0, title=""):
    mails, _ = mon.apply_status(e, res, T0 + timedelta(minutes=minutes), title)
    return mails


class SignatureTest(unittest.TestCase):
    def test_valid_and_invalid(self):
        raw = b'{"type":"test","environment":"e-drivebook.com","event":{}}'
        sig = "sha256=" + hmac.new(b"secret", raw, hashlib.sha256).hexdigest()
        self.assertTrue(mon.valid_signature("secret", raw, sig))
        self.assertFalse(mon.valid_signature("other", raw, sig))
        self.assertFalse(mon.valid_signature("secret", raw + b" ", sig))  # body changed
        self.assertFalse(mon.valid_signature("secret", raw, sig.replace("sha256=", "")))
        self.assertFalse(mon.valid_signature("secret", raw, None))
        self.assertFalse(mon.valid_signature("", raw, sig))  # no secret configured


class StateTest(unittest.TestCase):
    def test_up_down_up_one_mail_per_change(self):
        e = env()
        self.assertEqual(poll(e, Response(200, OK)), [])
        self.assertEqual(e.state, "up")
        # Two failures: still up, no e-mail
        self.assertEqual(poll(e, Response(0, error="TimeoutError: timed out"), 1), [])
        self.assertEqual(poll(e, Response(502, error="HTTP 502"), 2), [])
        self.assertEqual(e.state, "up")
        # Third failure in a row: DOWN, exactly one e-mail with the last error
        mails = poll(e, Response(0, error="URLError: connection refused"), 3)
        self.assertEqual(len(mails), 1)
        self.assertIn("НЕ ОТВЕЧАЕТ", mails[0].subject)
        self.assertIn("connection refused", mails[0].text)
        self.assertEqual(e.state, "down")
        # Still failing: nothing new
        self.assertEqual(poll(e, Response(0, error="x"), 4), [])
        self.assertEqual(poll(e, Response(503, error="HTTP 503"), 30), [])
        # Back: exactly one e-mail with the downtime
        mails = poll(e, Response(200, OK), 63)
        self.assertEqual(len(mails), 1)
        self.assertIn("снова работает", mails[0].subject)
        self.assertIn("1 ч 0 мин", mails[0].text)
        self.assertEqual((e.state, e.fail_count, e.down_since), ("up", 0, None))
        self.assertEqual(poll(e, Response(200, OK), 64), [])

    def test_status_down_is_down_at_once(self):
        e = env(state="up")
        mails = poll(e, Response(200, {"status": "down", "time": "x", "checks": {"database": {"ok": False, "detail": "no connection"}}}))
        self.assertEqual(len(mails), 1)
        self.assertIn("database: no connection", mails[0].text)
        self.assertEqual(e.state, "down")
        self.assertEqual(poll(e, Response(200, {"status": "down", "time": "x", "checks": {}}), 1), [])

    def test_failures_reset_by_a_good_poll(self):
        e = env(state="up")
        poll(e, Response(0, error="x"))
        poll(e, Response(0, error="x"), 1)
        poll(e, Response(200, OK), 2)
        self.assertEqual(poll(e, Response(0, error="x"), 3), [])
        self.assertEqual(e.state, "up")

    def test_degraded_mail_after_10_minutes_once(self):
        e = env(state="up")
        self.assertEqual(poll(e, Response(200, DEGRADED)), [])
        self.assertEqual(e.state, "degraded")
        self.assertEqual(poll(e, Response(200, DEGRADED), 9), [])
        mails = poll(e, Response(200, DEGRADED), 10)
        self.assertEqual(len(mails), 1)
        text = mails[0].text
        self.assertIn("check redis: connection refused", text)
        self.assertIn("job Reminders (stale)", text)
        self.assertIn("job Backup (error): disk full", text)
        self.assertNotIn("Fine", text)
        self.assertEqual(poll(e, Response(200, DEGRADED), 20), [])  # not repeated
        poll(e, Response(200, OK), 21)
        self.assertEqual(e.state, "up")
        # A new degraded period starts its own 10 minutes
        self.assertEqual(poll(e, Response(200, DEGRADED), 22), [])
        self.assertEqual(len(poll(e, Response(200, DEGRADED), 32)), 1)

    def test_401_once_and_not_down(self):
        e = env(state="up")
        mails = poll(e, Response(401, error="HTTP 401"))
        self.assertEqual(len(mails), 1)
        self.assertIn("неверный токен", mails[0].subject)
        self.assertEqual(e.state, "up")
        for i in range(5):  # many 401s: no more e-mails, never DOWN
            self.assertEqual(poll(e, Response(401), i + 1), [])
        self.assertEqual((e.state, e.fail_count), ("up", 0))
        poll(e, Response(200, OK), 10)
        self.assertFalse(e.token_invalid)

    def test_required_fields_only(self):
        # Another project may send only status, time and checks
        e = env()
        self.assertEqual(poll(e, Response(200, {"status": "ok", "time": "2026-11-05T08:00:00Z", "checks": {}})), [])
        self.assertEqual(e.state, "up")
        # Without them the answer counts as a failed poll
        for i, body in enumerate([{"time": "x", "checks": {}}, {"status": "fine", "time": "x", "checks": {}}, {"status": "ok", "checks": {}}]):
            poll(e, Response(200, body), i + 1)
        self.assertEqual(e.state, "down")
        self.assertIn("required", e.last_error)

    def test_project_name_in_subject(self):
        e = env(state="up")
        mails = poll(e, Response(200, {"status": "down", "time": "x", "checks": {}}), title="e-Drivebook · k2drive.com")
        self.assertEqual(mails[0].subject, "[e-Drivebook · k2drive.com] НЕ ОТВЕЧАЕТ")

    def test_404_api_off_is_not_down(self):
        e = env(state="up")
        self.assertEqual(poll(e, Response(404)), [])
        self.assertEqual(e.state, "off")


class SecretsTest(unittest.TestCase):
    def test_encrypted_with_key_plain_without(self):
        from cryptography.fernet import Fernet

        key = Fernet.generate_key().decode()
        with mock.patch.object(mon.settings, "monitoring_secret_key", key):
            sealed = mon.seal("tok")
            self.assertTrue(sealed.startswith("enc:"))
            self.assertNotIn("tok", sealed)
            self.assertEqual(mon.unseal(sealed), "tok")
            self.assertEqual(mon.seal(""), "")
            self.assertEqual(mon.unseal("plain-from-before"), "plain-from-before")
        with mock.patch.object(mon.settings, "monitoring_secret_key", ""):
            self.assertEqual(mon.seal("tok"), "tok")
            self.assertEqual(mon.unseal(sealed), "")  # key gone: must be entered again
        with mock.patch.object(mon.settings, "monitoring_secret_key", Fernet.generate_key().decode()), self.assertLogs("monitoring", "ERROR"):
            self.assertEqual(mon.unseal(sealed), "")  # other key


class ErrorsTest(unittest.TestCase):
    def test_dedup_by_id_and_count(self):
        known = {1: 3}
        items = [{"id": 1, "count": 3}, {"id": 2, "count": 1}]
        self.assertEqual([x["id"] for x in mon.changed_errors(known, items)], [2])
        self.assertEqual(mon.changed_errors(known, items), [])  # same answer again
        self.assertEqual([x["id"] for x in mon.changed_errors(known, [{"id": 1, "count": 5}])], [1])
        self.assertEqual(known, {1: 5, 2: 1})

    def test_cursor_since(self):
        items = [
            {"id": 3, "last_seen_at": "2026-11-05T08:10:00+00:00"},
            {"id": 2, "last_seen_at": "2026-11-05T08:30:00Z"},
            {"id": 1, "last_seen_at": "2026-11-05T07:00:00+00:00"},
        ]
        self.assertEqual(mon.next_cursor("", items), "2026-11-05T08:30:00Z")
        self.assertEqual(mon.next_cursor("2026-11-05T09:00:00+00:00", items), "2026-11-05T09:00:00+00:00")  # older items keep it
        self.assertEqual(mon.next_cursor("2026-11-05T09:00:00+00:00", []), "2026-11-05T09:00:00+00:00")

    def test_error_mail_every_30_minutes(self):
        self.assertTrue(mon.mail_due(None, T0))
        self.assertFalse(mon.mail_due(T0, T0 + timedelta(minutes=29)))
        self.assertTrue(mon.mail_due(T0, T0 + timedelta(minutes=30)))


def error(i, count, seen):
    return {"id": i, "source": "backend", "level": "ERROR", "logger_name": "app", "message": f"Boom {i}", "traceback": "Traceback…",
            "path": "/v1/bookings", "method": "POST", "user_id": None, "count": count, "first_seen_at": "2026-11-05T07:00:00Z",
            "last_seen_at": seen, "last_alerted_at": None, "resolved": False}


@unittest.skipUnless(importlib.util.find_spec("aiosqlite"), "needs aiosqlite for the in-memory database")
class GlueTest(unittest.IsolatedAsyncioTestCase):
    """poll_status / poll_errors / save_errors with a fake HTTP and an in-memory database."""

    async def asyncSetUp(self):
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

        from app.models import Base, MonitorEnv, MonitorProject

        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.Session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.mails = []

        async def fake_send(to, subject, text):
            self.mails.append(subject)
            return True

        self.patch = mock.patch.object(mon, "send_mail", fake_send)
        self.patch.start()
        self.db = self.Session()
        self.project = MonitorProject(name="e-Drivebook")
        self.db.add(self.project)
        await self.db.flush()
        self.env = MonitorEnv(project_id=self.project.id, name="test", kind="test", base_url="https://k2drive.com/v1/monitoring/external", api_token="tok", enabled=True)
        self.db.add(self.env)
        await self.db.commit()

    async def asyncTearDown(self):
        self.patch.stop()
        await self.db.close()
        await self.engine.dispose()

    def fetcher(self, answers):
        calls = []

        def fake(url, token):
            calls.append((url, token))
            return answers.pop(0)

        return fake, calls

    async def test_errors_poll_dedup_cursor_and_mail(self):
        from sqlalchemy import select

        from app.models import MonitorError

        first = [error(2, 1, "2026-11-05T08:20:00Z"), error(1, 4, "2026-11-05T08:00:00Z")]
        fake, calls = self.fetcher([Response(200, first), Response(200, first), Response(200, [error(1, 6, "2026-11-05T08:40:00Z")])])
        self.assertEqual(await mon.poll_errors(self.db, self.env, fake), 2)
        self.assertEqual(len(self.mails), 2)  # no webhook: e-mails come from polling
        self.assertEqual(self.env.errors_cursor, "2026-11-05T08:20:00Z")
        # The token goes to the request header (fetch), never into the URL
        self.assertNotIn("tok", calls[0][0])
        self.assertEqual(calls[0][1], "tok")
        # Same answer: nothing new; the cursor is sent
        self.assertEqual(await mon.poll_errors(self.db, self.env, fake), 0)
        self.assertIn("since=2026-11-05T08%3A20%3A00Z", calls[1][0])
        self.assertEqual(len(self.mails), 2)
        # Count grew within 30 minutes: stored, no second e-mail
        self.assertEqual(await mon.poll_errors(self.db, self.env, fake), 1)
        row = await self.db.scalar(select(MonitorError).where(MonitorError.remote_id == 1))
        self.assertEqual(row.count, 6)
        self.assertEqual(len(self.mails), 2)

    async def test_no_poll_mail_when_webhook_is_set(self):
        self.env.webhook_secret = "s"
        fake, _ = self.fetcher([Response(200, [error(9, 1, "2026-11-05T08:00:00Z")])])
        self.assertEqual(await mon.poll_errors(self.db, self.env, fake), 1)
        self.assertEqual(self.mails, [])
        # The webhook e-mails it (once per 30 min)
        await mon.save_errors(self.db, self.env, [error(9, 2, "2026-11-05T08:05:00Z")], "webhook", mail=True)
        await mon.save_errors(self.db, self.env, [error(9, 3, "2026-11-05T08:06:00Z")], "webhook", mail=True)
        self.assertEqual(len(self.mails), 1)

    async def test_status_poll_writes_history_and_mails(self):
        from sqlalchemy import select

        from app.models import MonitorEvent

        fails = [Response(0, error="timeout")] * 3
        fake, calls = self.fetcher([Response(200, OK), *fails, Response(200, OK)])
        for _ in range(5):
            await mon.poll_status(self.db, self.env, fake)
        self.assertTrue(calls[0][0].endswith("/status"))
        self.assertEqual(self.mails, ["[e-Drivebook · test] НЕ ОТВЕЧАЕТ", "[e-Drivebook · test] снова работает"])
        states = (await self.db.scalars(select(MonitorEvent.text).where(MonitorEvent.kind == "state"))).all()
        self.assertEqual([s.split(" · ")[0] for s in states], ["unknown → up", "up → down", "down → up"])
        self.assertEqual(json.loads(self.env.snapshot)["version"], "1.0.0")

    async def test_sealed_token_is_sent_decrypted(self):
        from cryptography.fernet import Fernet

        with mock.patch.object(mon.settings, "monitoring_secret_key", Fernet.generate_key().decode()):
            self.env.api_token = mon.seal("tok")
            fake, calls = self.fetcher([Response(200, OK)])
            await mon.poll_status(self.db, self.env, fake)
        self.assertEqual(calls[0][1], "tok")

    async def test_seed_once(self):
        from sqlalchemy import delete, select

        from app.models import MonitorEnv, MonitorProject

        await self.db.execute(delete(MonitorEnv))
        await self.db.execute(delete(MonitorProject))
        await mon.seed(self.db)
        envs = (await self.db.scalars(select(MonitorEnv).order_by(MonitorEnv.id))).all()
        self.assertEqual([(e.name, e.kind, e.enabled, e.api_token) for e in envs], [("e-drivebook.com", "production", False, ""), ("k2drive.com", "test", False, "")])
        self.assertEqual(envs[1].base_url, "https://k2drive.com/v1/monitoring/external")
        # Deleted by the user: not added again
        await self.db.execute(delete(MonitorEnv))
        await self.db.execute(delete(MonitorProject))
        await self.db.commit()
        await mon.seed(self.db)
        self.assertEqual((await self.db.scalars(select(MonitorProject))).all(), [])

    async def test_tick_polls_only_ready_envs_by_their_interval(self):
        from app.models import MonitorEnv, MonitorProject

        off = MonitorProject(name="Off", enabled=False)
        self.db.add(off)
        await self.db.flush()
        self.db.add_all([
            MonitorEnv(project_id=self.project.id, name="no-token", base_url="https://a/x", api_token="", enabled=True),
            MonitorEnv(project_id=off.id, name="project-off", base_url="https://b/x", api_token="t", enabled=True),
            MonitorEnv(project_id=self.project.id, name="disabled", base_url="https://c/x", api_token="t", enabled=False),
        ])
        await self.db.commit()
        urls = []

        def fake(url, token):
            urls.append(url)
            return Response(200, OK if url.split("?")[0].endswith("/status") else [])

        with mock.patch.object(mon, "SessionLocal", self.Session):
            await mon.tick(fake)
            self.assertEqual(sorted(u.split("?")[0] for u in urls), ["https://k2drive.com/v1/monitoring/external/errors", "https://k2drive.com/v1/monitoring/external/status"])
            await mon.tick(fake)  # within poll_interval_seconds: nothing
            self.assertEqual(len(urls), 2)


if __name__ == "__main__":
    unittest.main()
