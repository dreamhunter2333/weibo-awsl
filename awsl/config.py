import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    uid: str
    cookie_sub: str
    keyword: str
    max_page: int
    db_url: str
    ttl_time: int

    class Config:
        env_file = os.environ.get("ENV_FILE", ".env")


settings = Settings()
