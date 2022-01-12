from typing import Callable

from redis import StrictRedis, Redis, ConnectionPool

from app import config

pool = ConnectionPool(
    host=config.REDIS_SERVER,
    port=6379,
    password=config.REDIS_REQUIREPASS,
    decode_responses=True,
)

strict_redis_maker: Callable[[], Redis] = lambda: StrictRedis(connection_pool=pool)

redis_maker: Callable[[], Redis] = lambda: Redis(connection_pool=pool)
