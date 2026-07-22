from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str = "agencydesk"
    POSTGRES_PASSWORD: str = "agencydesk_secret"
    POSTGRES_DB: str = "agencydesk_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://agencydesk:agencydesk_secret@localhost:5432/agencydesk_db"
    SECRET_KEY: str = "super_secret_jwt_key_for_dev_only"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()