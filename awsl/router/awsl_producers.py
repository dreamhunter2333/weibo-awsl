import logging
from typing import List

from fastapi.responses import JSONResponse
from fastapi import status
from fastapi import APIRouter
from celery import Celery

from ..models import AwslProducer, DBSession
from ..config import settings, WB_PROFILE
from ..tools import Tools
from .models import ProducerItem, ProducerRes, Message


router = APIRouter()
_logger = logging.getLogger(__name__)


@router.get("/producers", response_model=List[ProducerRes])
def awsl_producers():
    session = DBSession()
    try:
        producers = session.query(AwslProducer).all()
        res = [{
            "uid": producer.uid,
            "name": producer.name
        } for producer in producers]
    except Exception as e:
        session.close()
        raise e
    return res


@router.post("/producers", response_model=bool, responses={404: {"model": Message}})
def add_awsl_producers(producer: ProducerItem):
    if not producer.uid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "uid is None"}
        )
    profile = Tools.wb_get(url=WB_PROFILE.format(producer.uid))
    if not profile or not profile.get("data", {}).get("user"):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "No weibo user uid = {}".format(producer.uid)}
        )
    session = DBSession()
    try:
        res = session.query(AwslProducer).filter(
            AwslProducer.uid == producer.uid).one_or_none()
        if res:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Weibo user uid = {} already exist".format(producer.uid)}
            )
        awsl_producer = AwslProducer(
            uid=producer.uid,
            keyword=producer.keyword or "",
            name=profile["data"]['user']["screen_name"],
            profile=profile["data"]['user'])
        session.add(awsl_producer)
        _logger.info("awsl add awsl_producer done %s" % awsl_producer.name)
        session.commit()
    except Exception as e:
        session.close()
        raise e
    app = Celery('awsl-tasks', broker=settings.broker)
    app.send_task("awsl_start.start_awsl")
    return True
