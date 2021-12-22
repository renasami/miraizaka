import os
import sys

workspace = os.path.abspath(
    os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
)
sys.path.append(workspace)

import unittest
import logging
from datetime import datetime

import cv2
import numpy as np  # noqa

from RaspberryPi.FaceDetection import FaceDetection, FaceBase, UncodedData
from face_ee_manager.schema import Direction


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.img = cv2.imread("tests/test.jpg")
        frame_width, frame_height, _ = self.img.shape
        # url = "http://192.168.0.117:8080/test"
        faceCascade_path = workspace + "/RaspberryPi/haarcascades/haarcascade_profileface.xml"
        config = {
            "send_http": False,
            "show_window": True,
            "frame_width": frame_width,
            "frame_height": frame_height,
            "profile_faceCascade_path": faceCascade_path
        }
        logging.basicConfig(level=logging.DEBUG)
        self.face_detection = FaceDetection(config=config)

    def setUp(self):
        meg = f"---{self._testMethodName}---"
        print(meg, end="")
        print("-" * (70 - len(meg)))
        self.time_begin = datetime.now()

    def tearDown(self):
        t = datetime.now() - self.time_begin
        print(f"\nin: {t.total_seconds():.3f}s", end="\n\n\n")

    def test_FaceDetection__detect_face(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        res = self.face_detection._FaceDetection__detect_face(
            gray,
            Direction.LEFT_FACE,
            self.face_detection.config.frame_width,
        )

        # print(res)
        self.assertEqual(
            res, [
                FaceBase(
                    pos_x=34,
                    pos_y=38,
                    width=160,
                    heigth=160,
                    direction=Direction.LEFT_FACE,
                )
            ]
        )

    def test_detect_face(self):

        res = self.face_detection.detect_face(
            self.img,
            self.face_detection.config.frame_width,
            self.face_detection.config.frame_height,
            self.face_detection.offset,
        )

        res2 = self.face_detection.detect_face(
            self.img,
            self.face_detection.config.frame_width,
            self.face_detection.config.frame_height,
            1,
        )

        # print(res)
        # print(res2)
        self.assertEqual(
            res, [
                FaceBase(
                    pos_x=4,
                    pos_y=8,
                    width=220,
                    heigth=220,
                    direction=Direction.LEFT_FACE,
                )
            ]
        )

        self.assertEqual(
            res2, [
                FaceBase(
                    pos_x=33,
                    pos_y=37,
                    width=162,
                    heigth=162,
                    direction=Direction.LEFT_FACE,
                )
            ]
        )

    def test_encode_to_HTTPFace(self):

        uncoded_data = {
            "datetime":
            datetime.now(),
            "img":
            self.img,
            "faces":
            self.face_detection.detect_face(
                self.img,
                self.face_detection.config.frame_width,
                self.face_detection.config.frame_height,
                self.face_detection.offset,
            )
        }
        data_list = [UncodedData(**uncoded_data)]

        def __test_encode_to_HTTPFace():
            for _ in range(100):
                res = self.face_detection.encode_to_HTTPFace(data_list)
            return res

        res = __test_encode_to_HTTPFace()
        # print(res[0])
        return res


if __name__ == "__main__":
    unittest.main(verbosity=0)
