import logging

from telegram_bot.telegram_bot import start_consuming

logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(name)s: %(message)s",
    level=logging.INFO
)

start_consuming()
