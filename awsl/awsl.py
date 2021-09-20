import awsl
import json
import time
import logging
from typing import List
import requests
import threading

from .config import settings
from .tools import SqlTools
from .wb import new_cookie_sub


_logger = logging.getLogger(__name__)
WB_DATA_URL = "https://weibo.com/ajax/statuses/mymblog?uid={}&page="
WB_COOKIE = "SUB={}"


class WbAwsl(object):

    def __init__(self) -> None:
        self.url = WB_DATA_URL.format(settings.uid)
        self.cookie_sub = ""
        self.keyword = settings.keyword
        self.max_page = settings.max_page
        self.ttl_time = settings.ttl_time
        self.dbpath = settings.dbpath
        self.init_db()
        _logger.info("awsl init done %s" % settings)

    def run(self):
        max_id = self.select_max_id()
        _logger.info("awsl run: max_id=%s" % max_id)
        sql_tools = SqlTools(self.dbpath)
        for wbdata in self.get_wbdata(max_id):
            try:
                self.update_db(sql_tools, wbdata)
            except Exception as e:
                _logger.error(e)
        sql_tools.close()
        threading.Timer(self.ttl_time, self.run).start()

    def start(self) -> None:
        threading.Timer(0, self.run).start()

    @property
    def headers(self) -> dict:
        if not self.cookie_sub:
            return {}
        return {
            "cookie": WB_COOKIE.format(self.cookie_sub)
        }

    def select_max_id(self) -> int:
        res = SqlTools(self.dbpath).auto_fetchone(
            "SELECT max(id) FROM awsl_log"
        )
        return res[0] if res and res[0] else 0

    def new_cookie_sub(self):
        self.cookie_sub = new_cookie_sub()

    def wb_get(self, url) -> List:
        try:
            res = requests.get(url=url, headers=self.headers)
            if res.headers.get("Content-Type") == "text/html":
                t = threading.Thread(target=self.new_cookie_sub)
                t.start()
                t.join()
                return self.wb_get(url)
            return res.json()["data"]["list"]
        except Exception as e:
            _logger.exception(e)
            return []

    def get_wbdata(self, max_id: int) -> dict:
        for page in range(1, self.max_page):
            for wbdata in self.wb_get(url=self.url + str(page)):
                if wbdata["id"] <= max_id:
                    break
                # TODO: 正则是不是更好
                if self.keyword not in wbdata["text"]:
                    continue
                yield wbdata
            time.sleep(10)

    def update_db(self, sql_tools: SqlTools, wbdata: dict) -> None:
        if not wbdata.get("retweeted_status", {}).get("pic_infos"):
            return
        _logger.info("awsl update db id=%s mblogid=%s" % (wbdata["id"], wbdata["mblogid"]))
        sql_tools.execute_commit(
            "INSERT INTO awsl_log VALUES ('%s', '%s', '%s')" % (
                wbdata["id"], wbdata["mblogid"], json.dumps(wbdata["retweeted_status"]["pic_infos"])
            )
        )

    def init_db(self) -> None:
        _logger.info("awsl init db")
        SqlTools(self.dbpath).auto_commit("""
            CREATE TABLE if not exists awsl_log (
                id int, mblogid text, pic_infos text
            )
        """)
