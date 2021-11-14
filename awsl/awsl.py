import json
import time
import logging
from typing import Any
import requests
import threading

from awsl.models import Tools

from .config import settings


_logger = logging.getLogger(__name__)
WB_DATA_URL = "https://weibo.com/ajax/statuses/mymblog?uid={}&page="
WB_SHOW_URL = "https://weibo.com/ajax/statuses/show?id={}"
WB_COOKIE = "SUB={}"


class WbAwsl(object):

    def __init__(self) -> None:
        self.url = WB_DATA_URL.format(settings.uid)
        self.cookie_sub = ""
        self.keyword = settings.keyword
        self.max_page = settings.max_page
        self.ttl_time = settings.ttl_time
        Tools.init_db()
        _logger.info("awsl init done %s" % settings)

    def run(self):
        max_id = Tools.select_max_id()
        _logger.info("awsl run: max_id=%s" % max_id)
        try:
            for wbdata in self.get_wbdata(max_id):
                try:
                    re_mblogid = Tools.update_mblog(wbdata)
                    re_wbdata = self.wb_get(WB_SHOW_URL.format(
                        re_mblogid)) if re_mblogid else {}
                    Tools.update_pic(wbdata, re_wbdata)
                except Exception as e:
                    _logger.exception(e)
        except Exception as e:
            _logger.exception(e)
        threading.Timer(self.ttl_time, self.run).start()

    def start(self) -> None:
        threading.Timer(0, self.run).start()

    def wb_get(self, url) -> Any:
        try:
            res = requests.get(url=url, headers={
                "cookie": WB_COOKIE.format(settings.cookie_sub)
            })
            return res.json()
        except Exception as e:
            _logger.exception(e)
            return None

    def get_wbdata(self, max_id: int) -> dict:
        for page in range(1, self.max_page):
            wbdatas = self.wb_get(url=self.url + str(page))
            wbdatas = wbdatas.get("data", {}).get(
                "list", []) if wbdatas else []
            for wbdata in wbdatas:
                if wbdata["id"] <= max_id:
                    break
                # TODO: 正则是不是更好
                if self.keyword not in wbdata["text"]:
                    continue
                yield wbdata
            time.sleep(10)
