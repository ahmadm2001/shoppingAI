import redis
from app.config.settings import get_settings

settings = get_settings()

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)


def get_redis():
    """Return the Redis client instance."""
    return redis_client
