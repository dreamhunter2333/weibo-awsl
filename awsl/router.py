import json
import random
import logging

from typing import Optional
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from .config import settings
from .tools import SqlTools

_logger = logging.getLogger(__name__)
WB_URL_PREFIX = "https://weibo.com/{}/"

router = APIRouter()


@router.get("/awsl")
def route_awsl(limit: Optional[int] = 10, offset: Optional[int] = 0):
    _logger.info("awsl get limit %s offest %s" % (limit, offset))
    wb_data = SqlTools(settings.dbpath).auto_fetchall(
        "SELECT * FROM awsl_log order by id desc limit {} offset {}".format(limit, offset)
    )
    res = []
    for d_id, mblogid, pic_infos in wb_data:
        res.extend([pic["mw2000"]["url"] for pic in json.loads(pic_infos).values()])
    return res


@router.get("/awsl_count")
def awsl_count_awsl():
    _logger.info("awsl get_count")
    res = SqlTools(settings.dbpath).auto_fetchone(
        "SELECT count(1) FROM awsl_log"
    )
    return res[0] if res else 0


@router.get("/wbrandom")
def awsl_wb_random():
    limit = 1
    offset = random.randint(0, awsl_count_awsl())
    _logger.info("awsl get limit %s offest %s" % (limit, offset))
    wb_data = SqlTools(settings.dbpath).auto_fetchall(
        "SELECT * FROM awsl_log order by id desc limit {} offset {}".format(limit, offset)
    )
    urls = [WB_URL_PREFIX.format(settings.uid) + mblogid for _, mblogid, _ in wb_data]
    url = urls[random.randint(0, len(urls) - 1)] if len(urls) > 1 else urls[0]
    return RedirectResponse(url)
