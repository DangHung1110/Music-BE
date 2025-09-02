
import os
import redis.asyncio as redis
from dotenv import load_dotenv
load_dotenv()

class RedisConfig:
    def __init__(self):
        self.REDIS_URL=os.getenv("REDIS_URL")
        self.REDIS_HOST = os.getenv("REDIS_HOST")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
        self.REDIS_DECODE_RESPONSES = True

        self.SESSION_EXPIRE_SECONDS = int(os.getenv("SESSION_EXPIRE_SECONDS"))
        self.TOKEN_BLACKLIST_EXPIRE_SECONDS = int(os.getenv("TOKEN_BLACKLIST_EXPIRE_SECONDS"))

redis.config = RedisConfig()
redis_client: redis.Redis = None

async def get_redis()-> redis.Redis:
    if redis_client is None:
        redis_client = redis.Redis(
            host = redis.config.REDIS_HOST,
            port = redis.config.REDIS_PORT,
            db = redis.config.REDIS_DB,
            password = redis.config.REDIS_PASSWORD,
            decode_responses = redis.config.REDIS_DECODE_RESPONSES,
            socket_connect_timeout = 5,
            socket_timeout = 5,
            retry_on_timeout = True,
        )
    return redis_client

async def close_redis():
    global redis_client:
    if redis_client:
        await redis_client.close()
        redis_client = None

        