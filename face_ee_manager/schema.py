from pydantic import BaseModel
from typing import Optional, Tuple, List, Union
from datetime import datetime
from enum import Enum
import numpy as np

RGB_ndarray_img = np.ndarray


class Direction(Enum):
    LEFT_FACE = 1
    FRONT_FACE = 0
    RIGHT_FACE = -1


class EntryOrExit(Enum):
    ENTRY = 0
    EXIT = 1


# ！！重要データ構造
class FaceBase(BaseModel):
    top: int
    right: int
    bottom: int
    left: int
    direction: Optional[Direction] = None
    frame_width: int
    frame_height: int


class FaceSchema(FaceBase):
    datetime: datetime


class HTTPFace(FaceSchema):
    img_base64: bytes


class HTTPFacePack(BaseModel):
    index: int
    total: int
    faces: List[HTTPFace]


class EntryExitRawBase(FaceSchema):
    identification: Union[int, str]


# ！！重要データ構造
class EntryExitRaw(EntryExitRawBase):
    pass


class EntryExitInRawDB(EntryExitRawBase):
    img_base64: bytes


class EntryExitRawDBCreate(EntryExitInRawDB):
    pass


# ！！重要データ構造
class EntryExitBase(BaseModel):
    datetime: datetime
    identify_id: Union[int, str]
    entry_or_exit: EntryOrExit


class EntryExit(EntryExitBase):
    pass


class EntryExitDBCreate(EntryExitBase):
    identify_id: int


class FaceDetectPrama(BaseModel):
    scaleFactor: float
    minNeighbors: int
    minSize: Tuple[int, int]


class SchedulerConfig(BaseModel):
    end_trigger_delay_sec: int = 3
    trigger_rate: int = 3
