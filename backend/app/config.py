from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    environment: str = "development"
    
    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
