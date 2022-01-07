from sqlalchemy_utils import database_exists, create_database

from app.db import base
from app.db.session import engine


def has_table(model_class):
    return model_class.metadata.tables[model_class.__tablename__].exists(engine)


def init_db(db_session):
    if not database_exists(engine.url):
        create_database(engine.url)

    if not has_table(base.User):
        base.Base.metadata.create_all(bind=engine)

    db_session.close()
