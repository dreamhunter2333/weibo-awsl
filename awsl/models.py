import json
import logging

from sqlalchemy import Column, String, INT, TEXT, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from .config import settings

_logger = logging.getLogger(__name__)
engine = create_engine(settings.db_url)
DBSession = sessionmaker(bind=engine)
Base = declarative_base(engine)


class Mblog(Base):
    __tablename__ = 'awsl_mblog'

    id = Column(String(255), primary_key=True)
    uid = Column(String(255), default=settings.uid)
    mblogid = Column(String(255))
    re_id = Column(String(255))
    re_mblogid = Column(String(255))
    re_user_id = Column(String(255))
    re_user = Column(TEXT)


class Pic(Base):
    __tablename__ = 'awsl_pic'

    id = Column(INT, primary_key=True, autoincrement=True)
    awsl_id = Column(String(255), ForeignKey('awsl_mblog.id'))
    sequence = Column(INT)
    pic_id = Column(String(255))
    pic_info = Column(TEXT)
    awsl_mblog = relationship("Mblog", backref="mblog_of_pic")


class Tools():

    @staticmethod
    def init_db() -> None:
        try:
            Base.metadata.create_all()
        except Exception as e:
            _logger.exception(e)

    @staticmethod
    def select_max_id() -> int:
        session = DBSession()
        mblog = session.query(func.max(Mblog.id)).one()
        session.close()
        return int(mblog[0]) if mblog and mblog[0] else 0

    @staticmethod
    def update_mblog(wbdata: dict) -> str:
        if not wbdata or not wbdata.get("retweeted_status"):
            return ""
        _logger.info("awsl update db mblog id=%s mblogid=%s" %
                     (wbdata["id"], wbdata["mblogid"]))
        session = DBSession()
        mblog = Mblog(
            id=wbdata["id"],
            mblogid=wbdata["mblogid"],
            re_id=wbdata["retweeted_status"]["id"],
            re_mblogid=wbdata["retweeted_status"]["mblogid"],
            re_user_id=wbdata["retweeted_status"]["user"]["id"],
            re_user=json.dumps(wbdata["retweeted_status"]["user"])
        )
        session.add(mblog)
        session.commit()
        session.close()
        return wbdata["retweeted_status"]["mblogid"]

    @staticmethod
    def update_pic(wbdata: dict, re_wbdata: dict) -> None:
        if not re_wbdata:
            return
        pic_infos = re_wbdata.get("pic_infos", {})
        session = DBSession()
        for sequence, pic_id in enumerate(re_wbdata.get("pic_ids", [])):
            session.add(Pic(
                awsl_id=wbdata["id"],
                sequence=sequence,
                pic_id=pic_id,
                pic_info=json.dumps(pic_infos[pic_id]),
            ))
        session.commit()
        session.close()
