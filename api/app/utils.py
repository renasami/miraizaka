import cv2
import numpy as np

import base64


def encode_img_to_base64(img):
    _, encing = cv2.imencode(".jpg", img)
    return base64.b64encode(encing.tobytes()).decode("utf-8")


def decode_img_base64(img_base64):
    return cv2.imdecode(np.fromstring(base64.b64decode(img_base64), dtype="uint8"), 1)
