from pydantic_settings import BaseSettings

from custom_types import LogLevels

class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_ADMIN_ID: int
    DATABASE_URL: str = "sqlite+aiosqlite:///telegram_group_manager.db"
    LOG_DIR: str = 'logs'
    LOG_LEVEL: LogLevels = 'INFO'
    
    class Config:
        env_file = ".env"


settings = Settings()
