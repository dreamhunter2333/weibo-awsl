import logging
import telebot

from telebot.types import InputMediaPhoto
from .config import settings

bot = telebot.AsyncTeleBot(settings.telebot_token)

_logger = logging.getLogger(__name__)


class TelegramBot(object):

    @staticmethod
    def send_photos(re_wbdata: dict) -> None:
        try:
            pic_infos = re_wbdata.get("pic_infos", {})
            bot.send_media_group(chat_id=settings.chat_id, media=[
                InputMediaPhoto(media=pic_infos[pic_id]["original"]["url"])
                for pic_id in re_wbdata.get("pic_ids", [])
            ])
        except Exception as e:
            _logger.exception(e)
