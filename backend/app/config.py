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
    # Time zone for users who have not opened the panel yet
    default_tz: str = "Europe/Bratislava"


settings = Settings()
