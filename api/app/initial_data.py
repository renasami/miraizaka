import logging

from app.db.utils import init_db, init_redis
from app.db.session import db_session
from app.db.redis_instance import strict_redis_maker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init():
    init_db(db_session)
    init_redis(db_session, strict_redis_maker())


def main():
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
