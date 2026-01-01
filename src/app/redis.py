# app/cache.py
import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from typing import Optional
from arq import create_pool
from arq.connections import RedisSettings, ArqRedis

from src.app.settings import get_settings

# -------------------- Globals --------------------
redis_pool: Optional[ArqRedis] = None         # For ARQ jobs
redis_client: Optional[redis.Redis] = None    # For FastAPI + general Redis ops
cache_backend: Optional[RedisBackend] = None  # FastAPI Cache backend


# -------------------- Startup --------------------
async def init_redis() -> None:
    """
    Initialize Redis connections for both FastAPI cache and ARQ worker queue.
    Call this inside FastAPI's startup event.
    """
    global redis_client, cache_backend, redis_pool

    settings = get_settings()

    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.redis.redis_host,
            port=settings.redis.redis_port,
            password=settings.redis.redis_password,
            db=settings.redis.redis_db,
            decode_responses=True,
        )
        try:
            pong = await redis_client.ping()
            print("Redis connected:", pong)
        except Exception as e:
            print("Redis connection failed:", e)
            raise

    # --- Setup FastAPI Cache ---
    cache_backend = RedisBackend(redis_client)
    FastAPICache.init(cache_backend, prefix="fastapi-cache")

    # --- Setup ARQ Redis Pool ---
    if redis_pool is None:
        redis_pool = await create_pool(
            RedisSettings(
                host=settings.redis.redis_host,
                port=settings.redis.redis_port,
                password=settings.redis.redis_password,
                database=settings.redis.redis_db,
            )
        )
        redis_pool.default_queue_name = f"arq:queue:{settings.app.project_name}"
        print(f"ARQ Redis pool initialized with queue: {redis_pool.default_queue_name}")


# -------------------- Shutdown --------------------
async def close_redis_pool() -> None:
    global redis_client, redis_pool

    if redis_client:
        await redis_client.close()
        redis_client = None
        print("Redis client closed.")

    if redis_pool:
        await redis_pool.close()
        redis_pool = None
        print("ARQ Redis pool closed.")


# -------------------- Utility --------------------
async def get_redis() -> redis.Redis:
    """
    Return the global Redis client (already initialized in startup).
    """
    global redis_client
    if redis_client is None:
        settings = get_settings()
        redis_client = redis.Redis(
            host=settings.redis.redis_host,
            port=settings.redis.redis_port,
            password=settings.redis.redis_password,
            db=settings.redis.redis_db,
            decode_responses=True,
        )
    return redis_client


async def get_redis_pool() -> ArqRedis:
    """
    Return the global ARQ Redis pool (already initialized in startup).
    """
    global redis_pool
    if redis_pool is None:
        settings = get_settings()
        redis_pool = await create_pool(
            RedisSettings(
                host=settings.redis.redis_host,
                port=settings.redis.redis_port,
                password=settings.redis.redis_password,
                database=settings.redis.redis_db,
            )
        )
        redis_pool.default_queue_name = f"arq:queue:{settings.app.project_name}"
    return redis_pool
