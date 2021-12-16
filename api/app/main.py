from fastapi import FastAPI, UploadFile, status, File
from fastapi.responses import JSONResponse
# import requests
import cv2
import numpy as np

from typing import List
import base64
from keys import NOTIFY
import requests
import time

from app.schema import HTTPFace

# from starlette.responses import FileResponse
# from models import FaceSchema

app = FastAPI()
last_access = time.time()


@app.get("/")
def read_root():
    return {"Hello": "World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.post("/test_post")
def test_post(x, y, w, h, cw, ch, file: UploadFile = File(...)):
    print("Testing")
    print(x, y, w, h, cw, ch)
    print(file.read())

    return JSONResponse(content=file.filename, status_code=status.HTTP_200_OK)


@app.post("/notify")
def notify(face_list: List[HTTPFace]):

    global last_access

    print(last_access, time.time())

    if time.time() - last_access < 5:
        return JSONResponse(status_code=status.HTTP_200_OK)
    else:
        last_access = time.time()

    size_li = []
    for i in face_list:
        size_li.append({"file_size": len(i.img_base64)})
        print(len(i.img_base64))
        print(type(i.img_base64))
        img = cv2.imdecode(
            np.fromstring(base64.b64decode(i.img_base64), dtype="uint8"), 1
        )
        # cv2.imwrite("/app/test.jpg", img)

    state = face_list[0].direction.value

    message = ""
    if state > 0: message = "入室"
    else: message = "退出"
    headers = {
        'Authorization': NOTIFY,
    }
    files = {
        'message': (None, message),
    }
    response = requests.post(
        'https://notify-api.line.me/api/notify', headers=headers, files=files
    )
    return response.status_code


@app.post("/test")
def test_p(face_list: List[HTTPFace]):
    size_li = []
    for i in face_list:
        size_li.append({"file_size": len(i.img_base64)})
        print(len(i.img_base64))
        print(type(i.img_base64))
        img = cv2.imdecode(
            np.fromstring(base64.b64decode(i.img_base64), dtype="uint8"), 1
        )
        cv2.imwrite("/app/test.jpg", img)
    return JSONResponse(content=size_li, status_code=status.HTTP_200_OK)
