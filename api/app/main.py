from fastapi import FastAPI,UploadFile,status,File
from fastapi.params import File
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
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
def test_post(x,y,w,h,cw,ch,file:UploadFile=File(...)):
    print("Testing")
    print(x,y,w,h,cw,ch)
    print(file.read())
    
    return JSONResponse(content=file.filename,status_code=status.HTTP_200_OK)

  
@app.post("/test")
def test_p(face_list: List[FaceSchema]):
    for i in face_list:
        print(i.json())
    return JSONResponse(status_code=status.HTTP_200_OK)
