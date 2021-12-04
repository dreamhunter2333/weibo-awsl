import os

from pydantic import BaseSettings

CHUNK_SIZE = 9


class Settings(BaseSettings):
    pika_url: str
    queue: str
    telebot_token: str
    chat_id: str
    http_url: str

    class Config:
        env_file = os.environ.get("ENV_FILE", ".env")


settings = Settings()
