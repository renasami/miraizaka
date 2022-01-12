from typing import List

from fastapi import APIRouter
from fastapi import status, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from face_ee_manager.schema import HTTPFace, HTTPFacePack
from app.utils import get_db
from app import crud

router = APIRouter()


@router.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@router.post("/post")
def test_post(db: Session = Depends(get_db)):
    # from datetime import datetime
    # ee = [EEAction.ENTRY, EEAction.EXIT]
    # time_li = [
    #     '2022-01-01 20:15:13',
    #     '2022-01-02 06:08:51',
    #     '2022-01-04 01:09:18',
    #     '2022-01-06 18:35:19',
    #     '2022-01-03 20:29:24',
    #     '2022-01-06 18:05:26',
    #     '2022-01-04 07:32:41',
    #     '2022-01-10 01:37:49',
    #     '2022-01-08 15:36:44',
    #     '2022-01-08 01:18:00',
    #     '2022-01-10 03:56:49',
    # ]
    # time_li.sort()
    # for i, time in zip(range(len(time_li)), time_li):
    #     obj_in = EECreate(
    #         time=datetime.strptime(time, "%Y-%m-%d %H:%M:%S"),
    #         user_id=1,
    #         action=ee[i % 2]
    #     )
    #     crud.ee_record.create(db, obj_in=obj_in)
    # a = crud.user.get_all_ungraduated_member(db)
    # for i in a:
    #     for j in i.ee_records:
    #         print(j.id)

    # r = Redis(host=config.REDIS_SERVER, port=6379, password=config.REDIS_REQUIREPASS)
    # r.hset("testhash", "k1", "v1")
    # r.delete("testhash")

    return {"test-post"}


@router.post("/test")
def test_p(face_list: List[HTTPFace]):
    size_li = []
    for i in face_list:
        size_li.append({"file_size": len(i.img_base64)})
        print(len(i.img_base64), type(i.img_base64))
        # img = decode_img(i.img_base64)
        # img = img[:, :, ::-1]
        # cv2.imwrite("/app/test1.jpg", img)
    return JSONResponse(content=size_li, status_code=status.HTTP_200_OK)


@router.post("/async")
def test_async(face_pack: HTTPFacePack):
    print(face_pack.json())
    return face_pack


@router.get("/redis")
def test_redis(db: Session = Depends(get_db)):
    from app.db.redis_instance import redis_maker, strict_redis_maker  # noqa
    from app.db.utils import init_redis  # noqa
    from datetime import datetime
    from app.crud.schemas.entry_exit_record import EntryExitRecordCreate as EECreate, EEAction
    obj_in = EECreate(time=datetime.now(), user_id=3, action=EEAction.EXIT)
    crud.ee_record.create(db, obj_in=obj_in)
    return "ok"
