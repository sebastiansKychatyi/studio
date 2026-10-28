from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:PASSWORD@localhost:5432/duo"
    cookie_name: str = "duo_session"
    cookie_secure: bool = True
    session_days: int = 30
    docs: bool = True


settings = Settings()
