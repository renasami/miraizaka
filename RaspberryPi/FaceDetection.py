import typing
import numpy as np
import cv2

import os
from datetime import date, datetime
import json
from pydantic import ValidationError
from pydantic.fields import T
import requests
import base64
from pydantic import BaseModel
from typing import Optional, Union, Tuple, List
import logging
import asyncio

from api.app.schema import Direction, FaceBase, HTTPFace
from api.app.utils import encode_img_to_base64


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
    img: np.ndarray
    faces: List[FaceBase]


class FaceDetection:
    def __init__(
        self,
        url: str = None,
        offset: int = 30,
        debug: bool = False,
        config: Union[FaceDetectionConfig, dict] = FaceDetectionConfig(),
    ) -> None:
        self.url = url
        self.offset = offset
        self.logger = logging.getLogger("FaceDetection")
        self.logger.setLevel(logging.INFO)
        self.uncoded_data_list: List[UncodedData] = []

        # configを設定
        if type(config) == dict:
            self.config = FaceDetectionConfig(**config)
        else:
            self.config = config
        self.config.debug = debug

        if self.config.send_http and not url:
            raise ValueError("need a valid url")

        # デバグモード
        if self.config.debug:
            self.logger.setLevel(logging.DEBUG)
            logging.getLogger("asyncio").setLevel(logging.DEBUG)
            logging.basicConfig(level=logging.DEBUG)

        # モデル読み込み
        if self.config.front_faceCascade_path is not None:
            if self.config.front_face_detect_prama is None:
                raise ValueError("not valid front face detect prama")
            else:
                self.front_faceCascade = self.profile_faceCascade = cv2.CascadeClassifier(
                    self.config.front_faceCascade_path
                )

        self.profile_faceCascade = cv2.CascadeClassifier(
            self.config.profile_faceCascade_path
        )

        self.logger.info("Create object")

    def __detect_face(
        self,
        img,
        direction: Direction,
        frame_width,
    ) -> List[FaceBase]:

        faceCascade = self.profile_faceCascade
        prama = self.config.left_face_detect_prama

        if direction == Direction.RIGHT_FACE:
            img = cv2.flip(img, 1)
            prama = self.config.right_face_detect_prama

        if direction == Direction.FRONT_FACE:
            prama = self.config.front_face_detect_prama

        faces = faceCascade.detectMultiScale(
            img,
            scaleFactor=prama.scaleFactor,
            minNeighbors=prama.minNeighbors,
            minSize=prama.minSize,
        )

        # データの変換np.ndarray => FaceBase
        faces_obj_list = []
        if type(faces) == np.ndarray:
            c = np.full((len(faces), 1), direction)
            faces = np.c_[faces, c]
            if direction == Direction.LEFT_FACE:
                for i in range(len(faces)):
                    faces[i, 0] = frame_width - faces[i, 0] - faces[i, 2]

            for (pos_x, pos_y, width, heigth, direction) in faces:
                faces_obj_list.append(
                    FaceBase(
                        pos_x=pos_x,
                        pos_y=pos_y,
                        width=width,
                        heigth=heigth,
                        direction=direction
                    )
                )

        return faces_obj_list

    def __encode_to_HTTPFace(
        self,
        uncoded_data_list: List[UncodedData],
    ) -> list:

        data = []

        for i in uncoded_data_list:
            for j in i.faces:
                roi_color = i.img[j.pos_y:j.pos_y + j.heigth, j.pos_x:j.pos_x + j.width]
                img_base64 = encode_img_to_base64(roi_color)
                face_obj = HTTPFace(
                    **j,
                    datetime=i.datetime,
                    img_base64=img_base64,
                    frame_width=self.config.frame_width,
                    frame_height=self.config.frame_height,
                )
                data.append(json.loads(face_obj.json()))

    def detect_face(
        self,
        img,
        frame_width,
        frame_height,
        offset,
    ) -> List[FaceBase]:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        r_faces = self.__detect_face(gray, Direction.RIGHT_FACE, frame_width)
        l_faces = self.__detect_face(gray, Direction.LEFT_FACE, frame_width)

        faces = r_faces + l_faces
        if self.config.front_faceCascade_path is not None:
            f_faces = self.__detect_face(img, Direction.LEFT_FACE, frame_width)
            faces += f_faces

        for face in faces:
            face.pos_x = (face.pos_x - offset) if (face.pos_x - offset) > 0 else 0
            face.pos_y = (face.pos_y - offset) if (face.pos_y - offset) > 0 else 0
            face.width = (face.width + offset * 2) \
                if (face.width + offset * 2) < frame_width else frame_width
            face.heigth = (face.heigth + offset * 2) \
                if (face.heigth + offset * 2) < frame_height else frame_height

        return faces

    async def sent_face_http(self, uncoded_data_list: List[UncodedData]):
        data = self.__encode_to_HTTPFace(uncoded_data_list)
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, requests.post, url=url, json=data)

        res = await future
        如果没成功的处理
        return res

    def write(self):
        ...

    def show_window(self) -> None:
        ...

    def start():
        ...


if __name__ == "__main__":
    url = "http://192.168.0.117:8080/test"

    config = {
        "send_http":
        False,
        "show_window":
        True,
        "profile_faceCascade_path":
        "miraizaka/RaspberryPi/haarcascades/haarcascade_profileface.xml"
    }
    logging.basicConfig(level=logging.INFO)
    face_detection = FaceDetection(config=config)
    print(face_detection.config.send_http)
    print(face_detection._FaceDetection__detect_face)
