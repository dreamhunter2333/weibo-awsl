import json
import logging
import requests

from typing import List
from sqlalchemy.sql import func

from .models import AwslProducer, Mblog, Pic, Base, DBSession
from .config import settings, WB_COOKIE

_logger = logging.getLogger(__name__)


class Tools:

    @staticmethod
    def wb_get(url) -> dict:
        try:
            res = requests.get(url=url, headers={
                "cookie": WB_COOKIE.format(settings.cookie_sub)
            })
            return res.json()
        except Exception as e:
            _logger.exception(e)
            return None

    @staticmethod
    def init_db() -> None:
        try:
            Base.metadata.create_all()
        except Exception as e:
            _logger.exception(e)

    @staticmethod
    def select_max_id(uid: str) -> int:
        session = DBSession()
        try:
            mblog = session.query(func.max(Mblog.id)).filter(
                Mblog.uid == uid).one()
        finally:
            session.close()
        return int(mblog[0]) if mblog and mblog[0] else 0

    @staticmethod
    def update_max_id(uid: str, max_id: int) -> None:
        session = DBSession()
        try:
            session.query(AwslProducer).filter(
                AwslProducer.uid == uid
            ).update({
                AwslProducer.max_id: str(max_id)
            })
            session.commit()
        finally:
            session.close()

    @staticmethod
    def update_mblog(awsl_producer: AwslProducer, wbdata: dict) -> str:
        if not wbdata:
            return ""
        origin_wbdata = wbdata.get("retweeted_status") or wbdata
        if not origin_wbdata.get("user"):
            return ""
        _logger.info("awsl update db mblog awsl_producer=%s id=%s mblogid=%s" %
                     (awsl_producer.name, wbdata["id"], wbdata["mblogid"]))
        session = DBSession()
        try:
            mblog = Mblog(
                id=wbdata["id"],
                uid=awsl_producer.uid,
                mblogid=wbdata["mblogid"],
                re_id=origin_wbdata["id"],
                re_mblogid=origin_wbdata["mblogid"],
                re_user_id=origin_wbdata["user"]["id"],
                re_user=json.dumps(origin_wbdata["user"])
            )
            session.add(mblog)
            session.commit()
        finally:
            session.close()

        return origin_wbdata["mblogid"]

    @staticmethod
    def update_pic(wbdata: dict, re_wbdata: dict) -> None:
        if not re_wbdata:
            return
        pic_infos = re_wbdata.get("pic_infos", {})
        session = DBSession()
        try:
            for sequence, pic_id in enumerate(re_wbdata.get("pic_ids", [])):
                session.add(Pic(
                    awsl_id=wbdata["id"],
                    sequence=sequence,
                    pic_id=pic_id,
                    pic_info=json.dumps(pic_infos[pic_id]),
                ))
            session.commit()
        finally:
            session.close()

    @staticmethod
    def find_all_awsl_producer() -> List[AwslProducer]:
        session = DBSession()
        try:
            awsl_producers = session.query(AwslProducer).all()
        finally:
            session.close()
        return awsl_producers
