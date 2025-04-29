from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_ADMIN_ID: int
    DATABASE_URL: str = 'sqlite+aiosqlite:///telegram_group_manager.db'
    TELEGRAM_GROUP_ID: int
    
    class Config:
        env_file = ".env"

settings = Settings()