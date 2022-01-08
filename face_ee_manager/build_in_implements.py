import base64
from typing import Optional, Tuple, List, Any

import cv2
import numpy as np

try:
    import face_recognition
except Exception:
    pass

from .abc_classes import BaseCamera, BaseFaceDetection, BaseEntryExitIO, BaseFaceIdentification, BaseEntryExitJudgement
from .schema import RGB_ndarray_img, FaceBase, EntryExitRawDBCreate, EntryExit
from . import message

err_msg = message.err


def make_diff_trigger():
    last_img = None

    def trigger(img):
        nonlocal last_img
        if last_img is None:
            last_img = img
            return False

        abs_im_diff = np.abs(img.astype(int) - last_img.astype(int))
        if np.average(abs_im_diff) > 5:
            last_img = img
            return True
        else:
            return False

    return trigger


class Cv2Camera(BaseCamera):
    def __init__(
        self,
        device_id: int = 0,
        path: Optional[str] = None,
        frame_width: int = 1280,
        frame_height: int = 720,
        fps: int = 30
    ) -> None:
        if path: self.cam = cv2.VideoCapture(path)
        else:
            self.cam = cv2.VideoCapture(device_id)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
            self.cam.set(cv2.CAP_PROP_FPS, fps)

        self._frame_width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._frame_height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._fps = int(self.cam.get(cv2.CAP_PROP_FPS))

    @property
    def frame_width(self):
        return self._frame_width

    @property
    def frame_height(self):
        return self._frame_height

    @property
    def fps(self):
        return self._fps

    def get_frame(self) -> Tuple[RGB_ndarray_img, ...]:
        ret, frame = self.cam.read()
        if frame is not None: frame = frame[:, :, ::-1]
        return frame, ret


class FaceRecogDetection(BaseFaceDetection):
    def __init__(
        self,
        resolution_zoom: Optional[float] = 0.25,
        range_zoom: Optional[Tuple[int, ...]] = (40, 30, 30, 30)
    ) -> None:

        if resolution_zoom is not None and not (0 < resolution_zoom <= 1):
            raise ValueError(err_msg.rz_value)

        self._resolution_zoom = resolution_zoom
        self.range_zoom = range_zoom

    @property
    def resolution_zoom(self) -> Optional[float]:
        return self._resolution_zoom

    @resolution_zoom.setter
    def resolution_zoom(self, val):
        self._resolution_zoom = val

    @property
    def range_zoom(self) -> Optional[Tuple[int, ...]]:
        return self._range_zoom

    @range_zoom.setter
    def range_zoom(self, val):
        le = len(val)

        if le == 1:
            self._r_tp = self._r_rt = self._r_bm = self._r_lt = val[0]
        elif le == 2:
            self._r_tp = self._r_bm = val[0]
            self._r_rt = self._r_lt = val[1]
        elif le == 3:
            self._r_tp, self._r_bm = val[0], val[2]
            self._r_rt = self._r_lt = val[1]
        elif le == 4:
            self._r_tp, self._r_rt, self._r_bm, self._r_lt = val
        else:
            val = None

        self._range_zoom = val

    def detect_face(self, img: RGB_ndarray_img) -> List[FaceBase]:
        height, width, _ = img.shape
        if self.resolution_zoom:
            r_z = self.resolution_zoom
            img = cv2.resize(img, (0, 0), fx=r_z, fy=r_z)  # yapf: disable

        face_locations = face_recognition.face_locations(img)

        face_list = []
        for (top, right, bottom, left) in face_locations:

            if self.resolution_zoom:
                (top, right, bottom, left) = \
                    map(lambda x: int(x / self.resolution_zoom), (top, right, bottom, left))

            if self.range_zoom:
                top = int(top - self._r_tp) if int(top - self._r_tp) > 0 else 0
                left = int(left - self._r_tp) if int(left - self._r_tp) > 0 else 0
                bottom = int(bottom + self._r_bm) \
                    if int(bottom + self._r_bm) < height else height
                right = int(right + self._r_rt) \
                    if int(right + self._r_rt) < width else width

            face_list.append(
                FaceBase(
                    top=top,
                    right=right,
                    bottom=bottom,
                    left=left,
                    frame_width=width,
                    frame_height=height,
                )
            )

        return face_list


class EntryExitIO(BaseEntryExitIO):
    def __init__(self) -> None:
        super().__init__()

    @property
    def raw_db_path(self):
        pass

    @property
    def db_path(self):
        pass

    def save_entry_exit_raw(self, entry_exit_db: EntryExitRawDBCreate) -> Any:
        pass

    def save_entry_exit(self, entry_exit_db_list: List[EntryExit]) -> Any:
        pass

    def encode_img(self, img) -> str:
        _, encing = cv2.imencode(".jpg", img)
        return base64.b64encode(encing.tobytes()).decode("utf-8")

    def decode_img(self, str) -> RGB_ndarray_img:
        return cv2.imdecode(np.fromstring(base64.b64decode(str), dtype="uint8"), 1)


class FaceIdentification(BaseFaceIdentification):
    @property
    def model(self):
        pass

    @model.setter
    def model(self, val):
        pass

    def identify_face(self, face_img: RGB_ndarray_img):
        pass


class EntryExitJudgement(BaseEntryExitJudgement):
    def judge_entry_exit(
        self,
        entry_exit_raw_list,
    ) -> List[EntryExit]:
        pass


class TorchFaceRecognition(BaseFaceIdentification):
    @property
    def model(self):
        pass

    @model.setter
    def model(self, val):
        pass

    def decode_base64(self, img_str: base64) -> RGB_ndarray_img:
        return base64.b64decode(img_str).decode()

    def identify_face(self, face_img: RGB_ndarray_img) -> int:
        pass
