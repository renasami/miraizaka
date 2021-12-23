from .build_in_implements import Cv2Camera, FaceRecogDetection, EntryExitIO  # noqa
from .scheduler import Scheduler  # noqa
from .schema import *

utils_io = EntryExitIO()


def encode_img(img: RGB_ndarray_img) -> str:
    return utils_io.encode_img(img)


def decode_img(img_base64: str) -> RGB_ndarray_img:
    return utils_io.decode_img(img_base64)
