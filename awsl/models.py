from sqlalchemy import Column, String, INT, JSON, TEXT, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .config import settings

engine = create_engine(settings.db_url, pool_size=100)
DBSession = sessionmaker(bind=engine)
Base = declarative_base(engine)


class AwslProducer(Base):
    __tablename__ = 'awsl_producer'

    id = Column(INT, primary_key=True, autoincrement=True)
    uid = Column(String(255), nullable=False)
    name = Column(String(255))
    keyword = Column(String(255))
    profile = Column(JSON)
    max_id = Column(String(255))


class Mblog(Base):
    __tablename__ = 'awsl_mblog'

    id = Column(String(255), primary_key=True)
    uid = Column(String(255))
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
