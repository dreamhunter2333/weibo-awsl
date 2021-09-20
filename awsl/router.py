import json
import random
import logging

from typing import Optional
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from .config import settings
from .tools import SqlTools

_logger = logging.getLogger(__name__)
WB_URL_PREFIX = "https://weibo.com/{}/{}"

router = APIRouter()


@router.get("/awsl")
def route_awsl(limit: Optional[int] = 10, offset: Optional[int] = 0):
    _logger.info("awsl get limit %s offest %s" % (limit, offset))
    wb_ids = SqlTools(settings.dbpath).auto_fetchall(
        "SELECT id FROM awsl_mblog order by id desc limit {} offset {}".format(
            limit, offset
        )
    )
    wb_ids = ["0"] + [str(wb_id[0]) for wb_id in wb_ids if wb_id]
    pic_infos = SqlTools(settings.dbpath).auto_fetchall(
        "SELECT pic_info FROM awsl_pic where awsl_id in ({}) order by awsl_id desc, sequence asc".format(
            ",".join(wb_ids)
        )
    )
    return [json.loads(pic[0])["mw2000"]["url"] for pic in pic_infos]


@router.get("/awsl_count")
def awsl_count():
    res = SqlTools(settings.dbpath).auto_fetchone(
        "SELECT count(1) FROM awsl_mblog"
    )
    _logger.info("awsl get_count %s", res)
    return res[0] if res else 0


@router.get("/list")
def awsl_list(limit: Optional[int] = 10, offset: Optional[int] = 0):
    _logger.info("list get limit %s offest %s" % (limit, offset))
    res = SqlTools(settings.dbpath).auto_fetchall(
        """SELECT re_user_id, re_mblogid, pic_info
        FROM awsl_pic
        JOIN awsl_mblog
        ON awsl_pic.awsl_id=awsl_mblog.id
        order by awsl_id desc, sequence asc limit {} offset {}
        """.format(
            limit, offset
        )
    )
    return [{
        "wb_url": WB_URL_PREFIX.format(str(re_user_id), re_mblogid),
        "pic_info": json.loads(pic_info)
    } for re_user_id, re_mblogid, pic_info in res]


@router.get("/list_count")
def awsl_list_count():
    res = SqlTools(settings.dbpath).auto_fetchone(
        "SELECT count(1) FROM awsl_pic"
    )
    _logger.info("awsl_list_count %s", res)
    return res[0] if res else 0


@router.get("/wbrandom")
def awsl_wb_random():
    limit = 1
    offset = random.randint(0, awsl_list_count())
    _logger.info("wbrandom get limit %s offest %s" % (limit, offset))
    wb_data = SqlTools(settings.dbpath).auto_fetchone(
        "SELECT re_user_id, re_mblogid FROM awsl_mblog order by id desc limit {} offset {}".format(
            limit, offset)
    )
    re_user_id, re_mblogid = wb_data
    url = WB_URL_PREFIX.format(str(re_user_id), re_mblogid)
    return RedirectResponse(url)
