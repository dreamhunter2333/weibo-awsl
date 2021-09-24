import awsl
import json
import time
import logging
from typing import Any, List
import requests
import threading

from .config import settings
from .tools import SqlTools
from .wb import new_cookie_sub


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
        self.dbpath = settings.dbpath
        self.init_db()
        _logger.info("awsl init done %s" % settings)

    def run(self):
        max_id = self.select_max_id()
        _logger.info("awsl run: max_id=%s" % max_id)
        sql_tools = SqlTools(self.dbpath)
        wbdatas = []
        try:
            wbdatas = self.get_wbdata(max_id)
        except Exception as e:
            _logger.exception(e)
        for wbdata in wbdatas:
            try:
                self.update_db(sql_tools, wbdata)
            except Exception as e:
                _logger.exception(e)
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
            "SELECT max(id) FROM awsl_mblog"
        )
        return res[0] if res and res[0] else 0

    def new_cookie_sub(self):
        self.cookie_sub = new_cookie_sub()

    def wb_get(self, url) -> Any:
        try:
            res = requests.get(url=url, headers=self.headers)
            if res.headers.get("Content-Type") == "text/html":
                t = threading.Thread(target=self.new_cookie_sub)
                t.start()
                t.join()
                return self.wb_get(url)
            return res.json()
        except Exception as e:
            _logger.exception(e)
            return None

    def get_wbdata(self, max_id: int) -> dict:
        for page in range(1, self.max_page):
            wbdatas = self.wb_get(url=self.url + str(page))
            wbdatas = wbdatas.get("data", {}).get("list", []) if wbdatas else []
            for wbdata in wbdatas:
                if wbdata["id"] <= max_id:
                    break
                # TODO: 正则是不是更好
                if self.keyword not in wbdata["text"]:
                    continue
                yield wbdata
            time.sleep(10)

    def update_db(self, sql_tools: SqlTools, wbdata: dict) -> None:
        if not wbdata.get("retweeted_status"):
            return
        _logger.info("awsl update db id=%s mblogid=%s" % (wbdata["id"], wbdata["mblogid"]))
        sql_tools.execute_commit(
            "INSERT INTO awsl_mblog VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (
                wbdata["id"], wbdata["mblogid"],
                wbdata["retweeted_status"]["id"], wbdata["retweeted_status"]["mblogid"],
                wbdata["retweeted_status"]["user"]["id"],
                json.dumps(wbdata["retweeted_status"]["user"])
            )
        )
        re_wbdata = self.wb_get(WB_SHOW_URL.format(wbdata["retweeted_status"]["mblogid"]))
        pic_infos = re_wbdata.get("pic_infos", {})
        for sequence, pic_id in enumerate(re_wbdata.get("pic_ids", [])):
            sql_tools.execute_commit(
                "INSERT INTO awsl_pic VALUES ('%s', '%s', '%s', '%s')" % (
                    wbdata["id"], sequence, pic_id, json.dumps(pic_infos[pic_id])
                )
            )

    def init_db(self) -> None:
        _logger.info("awsl init db")
        SqlTools(self.dbpath).auto_commit("""
            CREATE TABLE if not exists awsl_mblog (
                id int, mblogid text, re_id int, re_mblogid text, re_user_id int, re_user text
            );
        """)
        SqlTools(self.dbpath).auto_commit("""
            CREATE TABLE if not exists awsl_pic (
                awsl_id int, sequence int, pic_id text, pic_info text
            );
        """)
