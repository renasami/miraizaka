from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class Direction(Enum):
    LEFT_FACE = 1
    FRONT_FACE = 0
    RIGHT_FACE = -1

class FaceSchema(BaseModel):
    datetime: datetime
    pos_x: int
    pos_y: int
    width: int
    heigth: int
    direction: Direction
    img_base64: bytes
    frame_width: int
    frame_height: int