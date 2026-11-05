from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:PASSWORD@localhost:5432/duo"
    cookie_name: str = "duo_session"
    cookie_secure: bool = True
    session_days: int = 30
    docs: bool = True
    # Exchange rates for expenses: how much 1 EUR costs (edit in .env, restart the API)
    rate_uah: float = Field(51.5, gt=0)
    rate_usd: float = Field(1.16, gt=0)
    # Web Push (VAPID): python -m app.cli vapid prints a key pair; empty = push disabled
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:admin@example.com"
    # Calendars visible only to their owner; true = owners may share them (saved shares are kept)
    calendar_sharing: bool = False
    # SMTP for alert e-mails (monitoring); empty host = e-mails are only written to the log
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""  # empty = smtp_user
    smtp_security: str = "starttls"  # starttls | ssl | none
    # Project monitoring (monitoring.py)
    monitoring_alert_emails: str = "Kichatyisebastian@gmail.com"  # default recipients, comma separated
    monitoring_secret_key: str = ""  # Fernet key for tokens / webhook secrets in the DB (python -m app.cli fernet); empty = plain
    monitoring_errors_interval: int = Field(120, ge=30)  # seconds between /errors polls
    monitoring_admins: str = ""  # panel usernames allowed to open Monitoring, comma separated; empty = everyone
    # Time zone for users who have not opened the panel yet
    default_tz: str = "Europe/Bratislava"


settings = Settings()
