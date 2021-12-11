from fastapi import FastAPI,Body,status
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/test_post")
def test_post():
    
    return JSONResponse(status_code=status.HTTP_200_CREATED)

@app.post("/test")
def test():
    return True