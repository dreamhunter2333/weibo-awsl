import pika
import time
import json
import logging
import telebot
from telebot import apihelper

from telebot.types import InputMediaPhoto

from .config import CHUNK_SIZE, settings

_logger = logging.getLogger(__name__)

# telegram bot
bot = telebot.TeleBot(settings.telebot_token)
apihelper.proxy = {'https': settings.http_url}

# MQ
connection = pika.BlockingConnection(pika.URLParameters(settings.pika_url))
channel = connection.channel()
channel.queue_declare(queue=settings.queue, durable=True)


def send_photos(ch, method, properties, body) -> None:
    re_wbdata = json.loads(body)
    pic_infos = re_wbdata.get("pic_infos", {})
    pic_ids = re_wbdata.get("pic_ids", [])
    for i in range(0, len(pic_ids), CHUNK_SIZE):
        bot.send_media_group(chat_id=settings.chat_id, timeout=20, media=[
            InputMediaPhoto(media=pic_infos[pic_id]["original"]["url"])
            for pic_id in pic_ids[i:i+CHUNK_SIZE]
        ])
        _logger.info("send_media_group %s", pic_ids)
        time.sleep(10)
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(
    on_message_callback=send_photos,
    queue=settings.queue,
    auto_ack=False
)


def start_consuming() -> None:
    _logger.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
