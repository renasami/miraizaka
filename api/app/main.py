from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from typing import List

from app.schema import FaceSchema

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.post("/test_post")
def test_post(face_list: List[FaceSchema]):
    for i in face_list:
        print(i.json())
    return JSONResponse(status_code=status.HTTP_200_OK)
