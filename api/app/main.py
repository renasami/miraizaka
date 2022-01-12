import requests
import logging

from fastapi import FastAPI, Depends
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware

import cv2  # noqa: F401
import numpy as np  # noqa: F401
from sqlalchemy.orm import Session

from face_ee_manager.schema import HTTPFacePack, Direction, EntryExitRaw  # noqa: F401
from face_ee_manager import decode_img  # noqa: F401
from app.utils import FaceIdentification, EntryExitJudgement
from app import config
from app.db.session import session
from app.db.redis_instance import redis_maker
from app.utils import get_db
from app import crud
from app.crud.schemas.user import UserCreate, NowMember
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


@app.get("/get-now-member")
def get_now_member(db: Session = Depends(get_db)):
    r = redis_maker()
    now_member: dict[str, str] = r.hgetall("now_member")

    res = []
    for id, in_time in now_member.items():
        user = crud.user.get(db, id)
        res.append(NowMember(
            **jsonable_encoder(user),
            time=in_time,
        ))
    return res


@app.get("/get-all-ungraduated-member")
def get_all_ungraduated_member(db: Session = Depends(get_db)):
    return crud.user.get_all_ungraduated_member(db)


profile_faceCascade = cv2.CascadeClassifier(
    "/face_ee_manager/haarcascades/haarcascade_profileface.xml"
)
f_i = FaceIdentification()
f_j = EntryExitJudgement()
temp = []


@app.post("/receive_face_data")
def receive_face_data(face_pack: HTTPFacePack):
    global profile_faceCascade
    global temp

    li = []
    for face in face_pack.faces:
        img = decode_img(face.img_base64)
        gray = cv2.cvtColor(img[:, :, ::-1], cv2.COLOR_BGR2GRAY)
        profile_faces = profile_faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=2,
            minSize=(20, 20),
        )
        if type(profile_faces) == np.ndarray:
            print("L")
            face.direction = Direction.LEFT_FACE
        else:
            face.direction = Direction.RIGHT_FACE

        id = f_i.identify_face(img)
        li.append(EntryExitRaw(**face.dict(), identification=id))

    temp += li
    print(len(temp))
    if face_pack.index == face_pack.total:
        a = f_j.judge_entry_exit(temp)
        print(a)
        temp = []

    return li
