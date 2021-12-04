import pika
import time
import json
import logging
import telebot
import threading

from retry import retry
from telebot import apihelper

from telebot.types import InputMediaPhoto

from .config import CHUNK_SIZE, settings

_logger = logging.getLogger(__name__)

# telegram bot
bot = telebot.TeleBot(settings.telebot_token)
apihelper.proxy = {'https': settings.http_url}
lock = threading.Lock()


def send_photos(ch, method, properties, body) -> None:
    lock.acquire()
    try:
        re_wbdata = json.loads(body)
        pic_infos = re_wbdata.get("pic_infos", {})
        pic_ids = re_wbdata.get("pic_ids", [])
        for i in range(0, len(pic_ids), CHUNK_SIZE):
            bot.send_media_group(chat_id=settings.chat_id, timeout=20, media=[
                InputMediaPhoto(media=pic_infos[pic_id]["original"]["url"])
                for pic_id in pic_ids[i:i+CHUNK_SIZE]
            ])
            _logger.info("send_media_group %s", pic_ids)
            time.sleep(30)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    finally:
        lock.release()


@retry((pika.exceptions.AMQPConnectionError, telebot.apihelper.ApiTelegramException), delay=5, jitter=(1, 3), logger=_logger)
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
    except Exception as e:
        connection.close()
        raise e
