
import os
import redis.asyncio as redis
from dotenv import load_dotenv
load_dotenv()

class RedisConfig:
    def __init__(self):
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
        self.REDIS_DECODE_RESPONSES = True

        self.SESSION_EXPIRE_SECONDS = int(os.getenv("SESSION_EXPIRE_SECONDS", "1800"))
        self.TOKEN_BLACKLIST_EXPIRE_SECONDS = int(os.getenv("TOKEN_BLACKLIST_EXPIRE_SECONDS", "3600"))

redis_config = RedisConfig()
redis_client: redis.Redis = None

async def get_redis()-> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host = redis_config.REDIS_HOST,
            port = redis_config.REDIS_PORT,
            db = redis_config.REDIS_DB,
            password = redis_config.REDIS_PASSWORD,
            decode_responses = redis_config.REDIS_DECODE_RESPONSES,
            socket_connect_timeout = 5,
            socket_timeout = 5,
            retry_on_timeout = True,
        )
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None

        