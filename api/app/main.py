from fastapi import FastAPI, UploadFile, status, File
from fastapi.responses import JSONResponse
import cv2
# import numpy as np

from typing import List
# import base64
from keys import NOTIFY
import requests

from face_ee_manager.schema import HTTPFace
from face_ee_manager import decode_img

app = FastAPI()


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
def notify(state: int):
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
        img = decode_img(i.img_base64)
        img = img[:, :, ::-1]
        cv2.imwrite("/app/test1.jpg", img)
    return JSONResponse(content=size_li, status_code=status.HTTP_200_OK)


@app.post("/recognize")
def recognize():
    return 1