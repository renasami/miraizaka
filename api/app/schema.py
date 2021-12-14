from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class Direction(Enum):
    LEFT_FACE = 1
    FRONT_FACE = 0
    RIGHT_FACE = -1


class FaceBase(BaseModel):
    pos_x: int
    pos_y: int
    width: int
    heigth: int
    direction: Direction


class FaceSchema(FaceBase):
    datetime: datetime
    img_base64: bytes
    frame_width: int
    frame_height: int


class HTTPFace(FaceSchema):
    pass
