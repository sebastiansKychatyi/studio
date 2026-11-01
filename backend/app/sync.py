"""Offline edits replayed by the panel: the later change wins, and the user is told about it.

A queued request carries X-Offline-At (when the change was made, phone clock) and X-Client-Now
(phone clock when it is sent); their difference to the server clock corrects a wrong phone clock.
- The record changed on the server after the offline edit → 409, the newer change stays.
- It changed after the phone last saw it (X-Base-Updated) but before the edit → the edit is
  applied and the response says so (X-Overwrote: 1).
Requests without these headers (normal online use) are not affected.
"""

from datetime import datetime, timezone

from fastapi import HTTPException, Request, Response


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse(value: str) -> datetime | None:
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return _aware(d)


def _aware(d: datetime) -> datetime:
    # SQLite returns naive datetimes (UTC)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def check_offline(request: Request, response: Response, updated_at: datetime | None) -> None:
    at = _parse(request.headers.get("x-offline-at", ""))
    if at is None or updated_at is None:
        return
    sent = _parse(request.headers.get("x-client-now", ""))
    if sent is not None:
        at += utcnow() - sent
    current = _aware(updated_at)
    if current > at:
        raise HTTPException(409, "Changed on another device after this offline edit")
    base = _parse(request.headers.get("x-base-updated", ""))
    if base is not None and current > base:
        response.headers["X-Overwrote"] = "1"
