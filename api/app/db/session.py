from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .. import config

engine = create_engine(config.SQLALCHEMY_DATABASE_URI, encoding='UTF-8', echo=True)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
