import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    uid: str
    cookie_alc: str
    keyword: str
    max_page: int
    dbpath: str
    ttl_time: int

    class Config:
        env_file = os.environ.get("ENV_FILE", ".env")


settings = Settings()
