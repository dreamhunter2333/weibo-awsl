import pika
import time
import json
import logging
import telebot
import threading

from retry import retry
from telebot import apihelper

from telebot.types import InputMediaPhoto

from telegram_bot.LRU import LRU

from .config import settings

_logger = logging.getLogger(__name__)

# telegram bot
bot = telebot.TeleBot(settings.telebot_token)
apihelper.proxy = {'https': settings.http_url}
lock = threading.Lock()
failed_key = LRU()


def send_photos(ch, method, properties, body) -> None:
    lock.acquire()
    try:
        hash_body = hash(body)
        data = json.loads(body)
        pics = data.get("pics")
        wb_url = data.get("wb_url")
        awsl_producer = data.get("awsl_producer")
        caption = "#{} {}".format(awsl_producer, wb_url)
        if pics:
            bot.send_media_group(chat_id=settings.chat_id, timeout=20, media=[
                InputMediaPhoto(media=pic, caption=caption if index == 0 else None)
                for index, pic in enumerate(pics) if ".gif" not in pic
            ])
            _logger.info("send_media_group %s", pics)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        count = failed_key.get(hash_body, 0)
        failed_key.put(hash_body, count+1)
        if count >= 5:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            _logger.info("send body to %s", settings.queue+"_failed")
            ch.basic_publish(
                exchange='',
                routing_key=settings.queue+"_failed",
                body=body,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        raise e
    finally:
        lock.release()
        time.sleep(10)


@retry(Exception, delay=5, jitter=(1, 3), max_delay=50, logger=_logger)
def start_consuming():
    _logger.info('[*] Waiting for messages. To exit press CTRL+C')
    connection = pika.BlockingConnection(pika.URLParameters(settings.pika_url))
    channel = connection.channel()
    channel.queue_declare(queue=settings.queue, durable=True)
    channel.queue_declare(queue=settings.queue+"_failed", durable=True)
    channel.basic_consume(
        on_message_callback=send_photos,
        queue=settings.queue,
        auto_ack=False
    )
    try:
        channel.start_consuming()
    finally:
        connection.close()
