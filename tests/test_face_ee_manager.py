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
from face_ee_manager.build_in_implements import make_diff_trigger


def test_callback():
    a = 0

    def _test_callback(**kwargs):
        nonlocal a
        a += 1
        if a > 200:
            sys.exit(1)
        print("'a': %d, 'called_func': %s" % (a, kwargs["called_func"]))

    return _test_callback


is_skip = {
    "test_cv2_camera": False,
    "test_face_recog_detection": False,
    "test_io": False,
    "test_scheduler": False,
    "test_trigger": False,
}

is_skip["test_cv2_camera"] = True
is_skip["test_face_recog_detection"] = True
is_skip["test_io"] = True
is_skip["test_scheduler"] = True
# is_skip["test_trigger"] = True

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

    @unittest.skipIf(is_skip["test_cv2_camera"], "")
    @ddt.data(*camera)
    def test_cv2_camera(self, camera):
        cam = Cv2Camera(path=camera)
        print(cam.frame_width)
        print(cam.frame_height)
        print(cam.fps)
        for i in range(30):
            frame = cam.get_frame()[0]
            cv2.imshow('video', frame[:, :, ::-1])
            k = cv2.waitKey(30) & 0xff
            if k == 27:  # press 'ESC' to quit
                break

        cam.cam.release()
        cv2.destroyAllWindows()

    @unittest.skipIf(is_skip["test_face_recog_detection"], "")
    def test_face_recog_detection(self):
        cam = Cv2Camera(path="tests/testcase1.mp4")
        li = []
        while True:
            img, ret = cam.get_frame()
            if not ret:
                break

            f_d = FaceRecogDetection(resolution_zoom=0.25)
            li += f_d.detect_face(img[:, :, ::-1])

        print(li)

    @unittest.skipIf(is_skip["test_io"], "")
    def test_io(self):
        eeio = EntryExitIO()
        print(eeio)

    @unittest.skipIf(is_skip["test_scheduler"], "")
    def test_scheduler(self):
        cam = Cv2Camera(path="tests/testcase1.mp4")
        eeio = EntryExitIO()
        f_d = FaceRecogDetection(resolution_zoom=0.25)
        scheduler = Scheduler(
            camera_obj=cam,
            entry_exit_io_obj=eeio,
            face_detection_obj=f_d,
            face_identification_obj=None,
            entry_exit_judgement_obj=None,
            trigger=None,
            debug=True
        )
        scheduler.start(mode="sync")

    @unittest.skipIf(is_skip["test_trigger"], "")
    def test_trigger(self):
        trigger = make_diff_trigger()
        cam = Cv2Camera(path="tests/testcase1.mp4")
        frame, ret = cam.get_frame()
        while ret:
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame[:, :, ::-1], str(trigger(frame)), (0, 50), font, 1.0, (0, 0, 0), 1)
            cv2.imshow("video", frame[:, :, ::-1])
            k = cv2.waitKey(30) & 0xff
            if k == 27:  # press 'ESC' to quit
                break

            frame, ret = cam.get_frame()

        cam.cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    unittest.main(verbosity=0)
