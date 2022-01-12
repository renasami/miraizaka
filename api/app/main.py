import requests
import logging

from fastapi import FastAPI, Depends
from fastapi import Request, Response
from starlette.middleware.cors import CORSMiddleware

import cv2  # noqa
import numpy as np  # noqa
from sqlalchemy.orm import Session

from face_ee_manager.schema import HTTPFace, HTTPFacePack  # noqa: F401
from face_ee_manager import decode_img  # noqa: F401
from app import config
from app.db.session import session
from app.utils import get_db
from app import crud
from app.crud.schemas.user import UserCreate
from app.test_router import router as test_router

app = FastAPI(title=config.PROJECT_NAME)
app.include_router(test_router, prefix="/test", tags=["test"])
logger = logging.getLogger("uvicorn.error")


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response: Response = Response("Internal server error", status_code=500)
    try:
        request.state.db = session()
        logger.info("Get DB session")
        response = await call_next(request)

    finally:
        request.state.db.close()
        logger.info("Close DB session")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World!"}


@app.post("/notify")
def notify(state: int):
    message = ""
    if state > 0: message = "入室"
    else: message = "退出"
    headers = {
        'Authorization': config.NOTIFY,
    }
    files = {
        'message': (None, message),
    }
    response = requests.post(
        'https://notify-api.line.me/api/notify', headers=headers, files=files
    )
    return response.status_code


@app.post("/recognize")
def recognize():
    return 1


@app.post("/add-user")
def add_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return crud.user.create(db, obj_in=user_in)
