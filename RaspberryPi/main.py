import os
import sys

sys.path.append(
    os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "..")
)

import numpy as np
import cv2

from datetime import datetime
import json
from pydantic import ValidationError
import requests
import base64

from api.app.schema import Direction, HTTPFace

faceCascade_path = \
    os.path.dirname(os.path.abspath(__file__)) \
    + \
    os.path.sep + "haarcascades/haarcascade_profileface.xml"

profile_faceCascade = cv2.CascadeClassifier(faceCascade_path)


def get_profile_face(
    img, frame_width, frame_height, offset, scaleFactor, minNeighbors, minSize
):
    """imgの中の顔を検出して座標と右顔か左顔かを返す\n
    以下のように取り出すことができる\n
    for (pos_x, pos_y, width, heigth, direction) in returned_obj
        ...
    """
    def get_side_profile_face(img, opposite: bool):
        direction = Direction.LEFT_FACE
        if opposite:
            img = cv2.flip(img, 1)
            direction = Direction.RIGHT_FACE

        profile_faces = profile_faceCascade.detectMultiScale(
            img, scaleFactor=scaleFactor, minNeighbors=minNeighbors, minSize=minSize
        )

        if type(profile_faces) == np.ndarray:
            c = np.full((len(profile_faces), 1), direction)
            profile_faces = np.c_[profile_faces, c]

        if opposite:
            for i in range(len(profile_faces)):
                profile_faces[i, 0] = frame_width - profile_faces[i, 0] - profile_faces[i, 2]  # yapf:disable

        return profile_faces

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    profile_faces = get_side_profile_face(gray, False)
    profile_faces_opposite = get_side_profile_face(gray, True)

    if type(profile_faces) == np.ndarray and type(profile_faces_opposite) == np.ndarray:
        profile_faces = np.r_[profile_faces, profile_faces_opposite]
    else:
        if type(profile_faces_opposite) == np.ndarray:
            profile_faces = profile_faces_opposite

    for i in range(len(profile_faces)):

        profile_faces[i, 0] -= offset
        if profile_faces[i, 0] < 0:
            profile_faces[i, 0] = 0

        profile_faces[i, 1] -= offset
        if profile_faces[i, 1] < 0:
            profile_faces[i, 1] = 0

        profile_faces[i, 2] += offset * 2
        if profile_faces[i, 2] > frame_width:
            profile_faces[i, 2] = frame_width

        profile_faces[i, 3] += offset * 2
        if profile_faces[i, 3] > frame_height:
            profile_faces[i, 3] = profile_faces[i, 3]

    return profile_faces


def send_face(original_img, url, datetime, profile_faces, frame_width, frame_height):
    data = []

    for (pos_x, pos_y, width, heigth, direction) in profile_faces:
        roi_color = original_img[pos_y:pos_y + heigth, pos_x:pos_x + width]
        _, encing = cv2.imencode(".jpg", roi_color)
        img_str = encing.tostring()
        img_byte = base64.b64encode(img_str).decode("utf-8")

        face_dict = {
            "datetime": datetime,
            "pos_x": pos_x,
            "pos_y": pos_y,
            "width": width,
            "heigth": heigth,
            "direction": direction,
            "img_base64": img_byte,
            "frame_width": frame_width,
            "frame_height": frame_height
        }

        try:
            face_obj = HTTPFace(**face_dict)
        except ValidationError as e:
            print(e.json())

        data.append(json.loads(face_obj.json()))

    res = requests.post(url=url, json=data)
    return res.text


FRAME_WIDTH, FRAME_HEIGHT = 800, 450
# FRAME_WIDTH, FRAME_HEIGHT = 640, 360
# FRAME_WIDTH, FRAME_HEIGHT = 1280, 720
SCALE_FACTOR_PROFILE = 2.8
MIN_NEIGHBORS_PROFILE = 2
MIN_SIZE_PROFILE = (20, 20)
OFFSET = 30

SHOW_WINDOW = True

SAVE_PIC = True
SAVE_PIC = False

SEND_HTTP = True
SEND_HTTP = False

URL = "http://192.168.0.117:8080/test"
PATH = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "image"

if SAVE_PIC:
    PATH += "/{date}".format(date=datetime.now().strftime("%Y%m%d%H%M%s"))
    if not os.path.exists(PATH):
        os.mkdir(PATH)
    PATH += "/%s.jpg"


def main(n):
    def num_of_exec(n):
        while n:
            n -= 1
            yield n

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    li = ["width", "height", "fps"]

    for i in range(3):
        print(li[i], cap.get(i + 3))

    if SAVE_PIC:
        id = 0

    for i in num_of_exec(n):
        ret, img = cap.read()
        now = datetime.now()

        profile_faces = get_profile_face(
            img,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            OFFSET,
            SCALE_FACTOR_PROFILE,
            MIN_NEIGHBORS_PROFILE,
            MIN_SIZE_PROFILE
        )  # yapf: disable

        if SAVE_PIC:
            for (x, y, w, h, direction) in profile_faces:
                id += 1
                roi_color: np.ndarray = img[y:y + h, x:x + w]
                if roi_color.size != 0:
                    cv2.imwrite(PATH % id, roi_color)

        if SEND_HTTP and type(profile_faces) == np.ndarray:
            res = send_face(img, URL, now, profile_faces, FRAME_WIDTH, FRAME_HEIGHT)
            print(res)

        if SHOW_WINDOW:
            for (x, y, w, h, direction) in profile_faces:
                if direction is Direction.LEFT_FACE:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                elif direction is Direction.RIGHT_FACE:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

            cv2.imshow('video', img)
            k = cv2.waitKey(30) & 0xff
            if k == 27:  # press 'ESC' to quit
                break

    if SHOW_WINDOW:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main(10)
    print("end")
