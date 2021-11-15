import json
import random
import logging

from typing import Optional
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy.sql import func

from .models import AwslProducer, DBSession, Mblog, Pic
from .config import settings

_logger = logging.getLogger(__name__)
WB_URL_PREFIX = "https://weibo.com/{}/{}"

router = APIRouter()


@router.get("/producers")
def awsl_producers():
    session = DBSession()
    producers = session.query(AwslProducer).all()
    res = [{
        "uid": producer.uid,
        "name": producer.name
    } for producer in producers]
    session.close()
    return res


@router.get("/list")
def awsl_list(uid: Optional[str] = settings.uid, limit: Optional[int] = 10, offset: Optional[int] = 0):
    _logger.info("list get uid %s limit %s offest %s" % (uid, limit, offset))
    session = DBSession()
    pics = session.query(Pic).join(Mblog, Pic.awsl_id == Mblog.id).filter(Mblog.uid == uid).order_by(Pic.awsl_id.desc()).limit(limit).offset(offset).all()
    res = [{
        "wb_url": WB_URL_PREFIX.format(pic.awsl_mblog.re_user_id, pic.awsl_mblog.re_mblogid),
        "pic_info": json.loads(pic.pic_info)
    } for pic in pics if pic.awsl_mblog]
    session.close()
    return res


@router.get("/list_count")
def awsl_list_count(uid: Optional[str] = settings.uid):
    session = DBSession()
    res = session.query(func.count(Pic.id)).join(Mblog, Pic.awsl_id == Mblog.id).filter(Mblog.uid == uid).one()
    session.close()
    return int(res[0]) if res else 0


@router.get("/wbrandom")
def awsl_wb_random():
    session = DBSession()
    limit = 1
    awsl_count = session.query(func.count(Pic.id))
    offset = random.randint(0, awsl_count[0])
    _logger.info("wbrandom get limit %s offest %s" % (limit, offset))
    mblog = session.query(Mblog).limit(limit).offset(offset).all()
    url = WB_URL_PREFIX.format(mblog.re_user_id, mblog.re_mblogid)
    session.close()
    return RedirectResponse(url)
