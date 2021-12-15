import os
import sys

sys.path.append(
    os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "..")
)

import unittest
import logging

import cv2
import numpy as np  # noqa

from RaspberryPi.FaceDetection import FaceDetection, FaceBase
from api.app.schema import Direction


class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.img = cv2.imread("tests/test.jpg")
        frame_width, frame_height, _ = self.img.shape
        # url = "http://192.168.0.117:8080/test"
        config = {
            "send_http":
            False,
            "show_window":
            True,
            "frame_width":
            frame_width,
            "frame_height":
            frame_height,
            "profile_faceCascade_path":
            "/Users/chencheng/OneDrive/important/大学/授業資料/44情報科学総合演習/code/miraizaka/RaspberryPi/haarcascades/haarcascade_profileface.xml"
        }
        logging.basicConfig(level=logging.DEBUG)
        self.face_detection = FaceDetection(config=config)

        return super().setUp()

    def test_FaceDetection__detect_face(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        res = self.face_detection._FaceDetection__detect_face(
            gray,
            Direction.LEFT_FACE,
            self.face_detection.config.frame_width,
        )

        print(res)
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
            self.img, self.face_detection.config.frame_width,
            self.face_detection.config.frame_height, self.face_detection.offset
        )

        res2 = self.face_detection.detect_face(
            self.img, self.face_detection.config.frame_width,
            self.face_detection.config.frame_height, 1
        )

        print(res)
        print(res2)
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
