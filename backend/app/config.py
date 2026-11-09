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
    # Public site address, for "Open" buttons in Telegram (https only)
    site_url: str = ""
    # Telegram bot of the panel (@BotFather); empty = no bot
    telegram_bot_token: str = ""
    # Assistant: own messages are parsed by app/utils/quickParse.ts first (Node), the rest goes to the Claude CLI
    assistant_node: str = "node"  # empty = skip the parser
    assistant_claude: str = "claude"  # Claude Code CLI; empty = parser only
    assistant_claude_home: str = ""  # folder with one login per panel user: <folder>/<username> (CLAUDE_CONFIG_DIR)
    assistant_model: str = "haiku"
    assistant_timeout: int = Field(120, ge=20, le=600)  # seconds per Claude answer
    assistant_chat_model: str = "sonnet"  # default model of a new regular chat
    assistant_chat_timeout: int = Field(900, ge=60, le=3600)  # seconds per answer in a regular chat (code work)
    # Sandbox for code work: "" = none (no shell, no files), "docker" = Claude runs in container <prefix><username>
    assistant_sandbox: str = ""
    assistant_sandbox_prefix: str = "claude-"
    # How the container reaches the panel tools (MCP over HTTP); empty = SITE_URL
    assistant_sandbox_api: str = ""
    # The tools of the assistant call this API as the user (same machine)
    internal_api_url: str = "http://127.0.0.1:8000"


settings = Settings()
