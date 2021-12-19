from pydantic import BaseModel
from typing import Optional, Tuple, List, Any, Union
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


class FaceBase(BaseModel):
    top: int
    right: int
    bottom: int
    left: int
    direction: Optional[Direction]


class FaceSchema(FaceBase):
    datetime: datetime
    frame_width: int
    frame_height: int


class HTTPFace(FaceSchema):
    img_base64: bytes


class EntryExitRawBase(FaceSchema):
    identification: Union[int, str]


class EntryExitRaw(EntryExitRawBase):
    pass


class EntryExitInRawDB(EntryExitRawBase):
    img_base64: bytes


class EntryExitRawDBCreate(EntryExitInRawDB):
    pass


class EntryExitBase(BaseModel):
    datetime: datetime
    identify_id: Union[int, str]
    entry_or_exit: EntryOrExit


class EntryExitDBCreate(EntryExitBase):
    identify_id: int


class FaceDetectPrama(BaseModel):
    scaleFactor: float
    minNeighbors: int
    minSize: Tuple[int, int]


class FaceDetectionConfig(BaseModel):
    show_window: bool = False
    send_http: bool = True
    debug: bool = False
    frame_width: int = None
    frame_height: int = None
    front_faceCascade_path: Optional[str] = None
    profile_faceCascade_path: str = "./haarcascades/haarcascade_profileface.xml"
    front_face_detect_prama: Optional[FaceDetectPrama] = None
    right_face_detect_prama: FaceDetectPrama = FaceDetectPrama(
        scaleFactor=2, minNeighbors=3, minSize=(20, 20)
    )
    left_face_detect_prama: FaceDetectPrama = FaceDetectPrama(
        scaleFactor=2, minNeighbors=3, minSize=(20, 20)
    )


class UncodedData(BaseModel):
    datetime: datetime
    img: Any
    faces: List[FaceBase]
