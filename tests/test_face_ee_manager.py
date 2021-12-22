import os
import sys

workspace = os.path.abspath(
    os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".."
)
sys.path.append(workspace)

import ddt
import unittest
import logging
from datetime import datetime

import cv2

from face_ee_manager import Cv2Camera, FaceRecogDetection, EntryExitIO, Scheduler


def test_callback():
    a = 0

    def _test_callback(**kwargs):
        nonlocal a
        a += 1
        if a > 200:
            sys.exit(1)
        print("'a': %d, 'called_func': %s" % (a, kwargs["called_func"]))

    return _test_callback


camera = [None, "tests/testcase1.mp4"]


@ddt.ddt
class Test(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        print("===================================================")
        logging.basicConfig(level=logging.DEBUG)

    def setUp(self):
        meg = f"---{self._testMethodName}---"
        print(meg, end="")
        print("-" * (70 - len(meg)))
        self.time_begin = datetime.now()

    def tearDown(self):
        t = datetime.now() - self.time_begin
        print(f"\nin: {t.total_seconds():.3f}s", end="\n\n\n")

    @ddt.data(*camera)
    def test_cv2_camera(self, camera):
        cam = Cv2Camera(path=camera)
        print(cam.frame_width)
        print(cam.frame_height)
        print(cam.fps)
        for i in range(30):
            flame = cam.get_flame()[0]
            cv2.imshow('video', flame[:, :, ::-1])
            k = cv2.waitKey(30) & 0xff
            if k == 27:  # press 'ESC' to quit
                break

        cam.cam.release()
        cv2.destroyAllWindows()

    def test_face_recog_detection(self):
        cam = Cv2Camera(path="tests/testcase1.mp4")
        li = []
        while True:
            img, ret = cam.get_flame()
            if not ret:
                break

            f_d = FaceRecogDetection(resolution_zoom=0.25)
            li += f_d.detect_face(img[:, :, ::-1])

        print(li)

    def test_io(self):
        eeio = EntryExitIO()
        print(eeio)

    def test_scheduler(self):
        cam = Cv2Camera(path="tests/testcase1.mp4")
        eeio = EntryExitIO()
        f_d = FaceRecogDetection(resolution_zoom=0.25)
        scheduler = Scheduler(
            camera_obj=cam,
            entry_exit_io_obj=eeio,
            face_detection_obj=f_d,
            callback=test_callback(),
            debug=True
        )
        scheduler.start(mode="sync")


if __name__ == "__main__":
    unittest.main(verbosity=0)
