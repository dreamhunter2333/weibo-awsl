import os

from pydantic import BaseSettings


WB_DATA_URL = "https://weibo.com/ajax/statuses/mymblog?uid={}&page="
WB_SHOW_URL = "https://weibo.com/ajax/statuses/show?id={}"
WB_COOKIE = "SUB={}"
WB_PROFILE = "https://weibo.com/ajax/profile/info?uid={}"
WB_URL_PREFIX = "https://weibo.com/{}/{}"
WB_COOKIE = "SUB={}"
CHUNK_SIZE = 9


class Settings(BaseSettings):
    uid: str
    cookie_sub: str
    max_page: int
    db_url: str
    broker: str
    pika_url: str
    queue: str

    class Config:
        env_file = os.environ.get("ENV_FILE", ".env")


settings = Settings()
