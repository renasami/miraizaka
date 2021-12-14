from fastapi import FastAPI, UploadFile, status, File
from fastapi.responses import JSONResponse
# import requests
# import cv2
# import numpy as np

from typing import List
import base64

import requests

from app.schema import HTTPFace

from starlette.responses import FileResponse
from models import FaceSchema


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
def notify(state:int):
    message = ""
    if state > 0:message = "入室" 
    else:message = "退出"
    headers = {
        'Authorization': 'Bearer ltVMrvi3LqMYY3Cbd7p0fgBHEdvoLaW3Px8rMeugo7X',
    }
    files = {
        'message': (None,message ),
    }
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, files=files)
    return response.status_code

        


@app.post("/test")
def test_p(face_list: List[HTTPFace]):
    size_li = []
    for i in face_list:
        size_li.append({"file_size": len(i.img_base64)})
        print(len(i.img_base64))
        print(type(i.img_base64))
        img = cv2.imdecode(np.fromstring(base64.b64decode(i.img_base64), dtype="uint8"), 1)
        cv2.imwrite("/app/test.jpg", img)
    return JSONResponse(content=size_li, status_code=status.HTTP_200_OK)
