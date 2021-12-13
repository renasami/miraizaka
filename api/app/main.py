from fastapi import FastAPI,UploadFile,status,File
from fastapi.params import File
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
from models import FaceSchema

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/test_post")
def test_post(data:FaceSchema):
    
    print(data)
    
    return JSONResponse(status_code=status.HTTP_200_OK)
