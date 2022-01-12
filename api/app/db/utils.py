from sqlalchemy_utils import database_exists, create_database
from redis import Redis

from app.db import base
from app.db.session import engine
from app.db.models import EEAction, EntryExitRecord
from app import crud


def has_table(model_class):
    return model_class.metadata.tables[model_class.__tablename__].exists(engine)


def init_db(db_session):
    if not database_exists(engine.url):
        create_database(engine.url)

    if not has_table(base.User):
        base.Base.metadata.create_all(bind=engine)

    db_session.close()


def init_redis(db_session, redis_instance: Redis):
    redis_instance.delete("now_member")
    ungraduated_members = crud.user.get_all_ungraduated_member(db_session)

    for member in ungraduated_members:
        if not member.ee_records:
            continue

        status: EntryExitRecord = member.ee_records[-1]
        if status.action == EEAction.ENTRY:
            redis_instance.hset(
                "now_member",
                member.id,
                str(status.time),
            )
