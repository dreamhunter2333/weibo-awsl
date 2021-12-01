import re
import time
import logging
import threading

from .tools import Tools
from .telegram_bot import TelegramBot

from .config import settings, WB_DATA_URL, WB_SHOW_URL


_logger = logging.getLogger(__name__)
WB_EMO = re.compile(r'\[.*?\]')


class WbAwsl(object):

    def __init__(self, awsl_producer) -> None:
        self.awsl_producer = awsl_producer
        self.uid = awsl_producer.uid
        self.max_id = int(awsl_producer.max_id) if awsl_producer.max_id else 0
        self.url = WB_DATA_URL.format(awsl_producer.uid)
        self.keyword = awsl_producer.keyword
        Tools.init_db()
        _logger.info("awsl init done %s" % awsl_producer)

    @staticmethod
    def start() -> None:
        awsl_producers = Tools.find_all_awsl_producer()
        threads = []
        for awsl_producer in awsl_producers:
            awsl = WbAwsl(awsl_producer)
            t = threading.Thread(target=awsl.run)
            threads.append(t)
            t.start()

        # wating for all task down
        for t in threads:
            t.join()

        _logger.info("awsl run all awsl_producers done")

    def run(self) -> None:
        max_id = self.max_id or Tools.select_max_id(self.uid)
        _logger.info("awsl run: uid=%s max_id=%s" % (self.uid, max_id))
        try:
            for wbdata in self.get_wbdata(max_id):
                if wbdata["id"] > max_id:
                    Tools.update_max_id(self.uid, wbdata["id"])
                    max_id = wbdata["id"]
                try:
                    re_mblogid = Tools.update_mblog(self.awsl_producer, wbdata)
                    re_wbdata = Tools.wb_get(WB_SHOW_URL.format(
                        re_mblogid)) if re_mblogid else {}
                    TelegramBot.send_photos(re_wbdata)
                    Tools.update_pic(wbdata, re_wbdata)
                except Exception as e:
                    _logger.exception(e)
        except Exception as e:
            _logger.exception(e)
        _logger.info("awsl run: uid=%s done" % self.uid)

    def get_wbdata(self, max_id: int) -> dict:
        for page in range(1, settings.max_page):
            wbdatas = Tools.wb_get(url=self.url + str(page))
            wbdatas = wbdatas.get("data", {}).get(
                "list", []) if wbdatas else []

            if not wbdatas:
                return

            for wbdata in wbdatas:
                if wbdata["id"] <= max_id and page == 1:
                    continue
                elif wbdata["id"] <= max_id:
                    return
                # TODO: 正则是不是更好
                text_raw = WB_EMO.sub("", wbdata["text_raw"])
                if self.keyword not in text_raw:
                    continue
                yield wbdata
            time.sleep(10)
