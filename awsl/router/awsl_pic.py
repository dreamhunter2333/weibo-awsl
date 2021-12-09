import json
import logging

from typing import List, Optional
from fastapi import APIRouter
from sqlalchemy.sql import func
from fastapi.responses import JSONResponse

from ..models import DBSession, Mblog, Pic
from ..config import settings, WB_URL_PREFIX
from .models import Message, PicItem


router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/list", response_model=List[PicItem], responses={404: {"model": Message}})
def awsl_list(uid: Optional[str] = "", limit: Optional[int] = 10, offset: Optional[int] = 0):
    if limit > 1000:
        return JSONResponse(
            status_code=404,
            content={"message": "to large limit = {}".format(limit)}
        )
    _logger.info("list get uid %s limit %s offest %s" % (uid, limit, offset))
    session = DBSession()
    try:
        pics = session.query(Pic).join(Mblog, Pic.awsl_id == Mblog.id).filter(
            Mblog.uid == uid
        ).order_by(Pic.awsl_id.desc()).limit(limit).offset(offset).all() if uid else session.query(Pic).join(
            Mblog, Pic.awsl_id == Mblog.id).order_by(Pic.awsl_id.desc()).limit(limit).offset(offset).all()
        res = [{
            "wb_url": WB_URL_PREFIX.format(pic.awsl_mblog.re_user_id, pic.awsl_mblog.re_mblogid),
            "pic_info": json.loads(pic.pic_info)
        } for pic in pics if pic.awsl_mblog]
    finally:
        session.close()
    return res


@router.get("/list_count", response_model=int)
def awsl_list_count(uid: Optional[str] = "") -> int:
    session = DBSession()
    try:
        res = session.query(func.count(Pic.id)).join(
                Mblog, Pic.awsl_id == Mblog.id
            ).filter(
                Mblog.uid == uid
            ).one() if uid else session.query(func.count(Pic.id)).join(
                Mblog, Pic.awsl_id == Mblog.id
            ).one()
    finally:
        session.close()
    return int(res[0]) if res else 0
