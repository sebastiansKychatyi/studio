"""Plain-text e-mail over SMTP (settings SMTP_*). Without SMTP_HOST the message is only logged."""

import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage

from .config import settings

log = logging.getLogger("mail")


def configured() -> bool:
    return bool(settings.smtp_host)


def _send(to: list[str], subject: str, text: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject
    msg.set_content(text)
    context = ssl.create_default_context()
    if settings.smtp_security == "ssl":
        server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=20, context=context)
    else:
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20)
    with server:
        if settings.smtp_security == "starttls":
            server.starttls(context=context)
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)


async def send_mail(to: list[str], subject: str, text: str) -> bool:
    """True when handed to the SMTP server. Never raises (alerts must not break the poller)."""
    if not to:
        return False
    if not configured():
        log.warning("SMTP not configured, e-mail not sent: %s", subject)
        return False
    try:
        await asyncio.to_thread(_send, to, subject, text)
        return True
    except Exception:  # noqa: BLE001 - logged, the caller records it
        log.exception("e-mail failed: %s", subject)
        return False
