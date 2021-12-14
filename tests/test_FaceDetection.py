import unittest
import logging

import cv2
import numpy as np  # noqa

from RaspberryPi.FaceDetection import FaceDetection, FaceBase
from api.app.schema import Direction


class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.img = cv2.imread("tests/test.jpg")
        return super().setUp()

    def test_FaceDetection__detect_face(self):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        # url = "http://192.168.0.117:8080/test"
        frame_width, frame_height, _ = self.img.shape
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
        logging.basicConfig(level=logging.INFO)
        face_detection = FaceDetection(config=config)
        res = face_detection._FaceDetection__detect_face(
            gray,
            Direction.LEFT_FACE,
            frame_width,
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
        # url = "http://192.168.0.117:8080/test"
        frame_width, frame_height, _ = self.img.shape
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
        logging.basicConfig(level=logging.INFO)
        face_detection = FaceDetection(config=config)
        res = face_detection.detect_face(
            self.img, face_detection.config.frame_width,
            face_detection.config.frame_height, face_detection.offset
        )

        res2 = face_detection.detect_face(
            self.img, face_detection.config.frame_width,
            face_detection.config.frame_height, 1
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
    unittest.main()
