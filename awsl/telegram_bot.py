import logging
import telebot
from telebot import apihelper

from telebot.types import InputMediaPhoto
from .config import settings

bot = telebot.TeleBot(settings.telebot_token)
apihelper.proxy = {'https': settings.http_url}


_logger = logging.getLogger(__name__)


class TelegramBot(object):

    @staticmethod
    def send_photos(re_wbdata: dict) -> None:
        try:
            pic_infos = re_wbdata.get("pic_infos", {})
            bot.send_media_group(chat_id=settings.chat_id, timeout=15, media=[
                InputMediaPhoto(media=pic_infos[pic_id]["original"]["url"])
                for pic_id in re_wbdata.get("pic_ids", [])
            ])
        except Exception as e:
            _logger.exception(e)
