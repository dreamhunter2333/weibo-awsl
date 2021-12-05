import pika
import time
import json
import logging
import telebot
import threading

from retry import retry
from telebot import apihelper

from telebot.types import InputMediaPhoto

from .config import settings

_logger = logging.getLogger(__name__)

# telegram bot
bot = telebot.TeleBot(settings.telebot_token)
apihelper.proxy = {'https': settings.http_url}
lock = threading.Lock()


def send_photos(ch, method, properties, body) -> None:
    lock.acquire()
    try:
        pics = json.loads(body)
        bot.send_media_group(chat_id=settings.chat_id, timeout=20, media=[
            InputMediaPhoto(media=pic)
            for pic in pics
        ])
        _logger.info("send_media_group %s", pics)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    finally:
        lock.release()
        time.sleep(10)


@retry(Exception, delay=5, jitter=(1, 3), logger=_logger)
def start_consuming():
    _logger.info('[*] Waiting for messages. To exit press CTRL+C')
    connection = pika.BlockingConnection(pika.URLParameters(settings.pika_url))
    channel = connection.channel()
    channel.queue_declare(queue=settings.queue, durable=True)
    channel.basic_consume(
        on_message_callback=send_photos,
        queue=settings.queue,
        auto_ack=False
    )
    try:
        channel.start_consuming()
    finally:
        connection.close()
