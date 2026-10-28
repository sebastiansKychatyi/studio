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


settings = Settings()
