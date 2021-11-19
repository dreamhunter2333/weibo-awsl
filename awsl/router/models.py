from pydantic import BaseModel


class ProducerItem(BaseModel):
    uid: str
    keyword: str


class ProducerRes(BaseModel):
    uid: str
    name: str


class PicItem(BaseModel):
    wb_url: str
    pic_info: dict


class Message(BaseModel):
    message: str
