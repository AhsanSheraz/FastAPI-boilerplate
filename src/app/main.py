from fastapi import FastAPI
import redis.asyncio as redis

from app.core.database import Base
from app.core.database import async_engine as engine
from app.core.config import settings
from app.api import router
from app.core import cache

# -------------- database --------------
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# -------------- cache --------------
async def create_redis_cache_pool():
    cache.pool = redis.ConnectionPool.from_url(settings.REDIS_CACHE_URL)
    cache.client = redis.Redis.from_pool(cache.pool)


async def close_redis_cache_pool():
    await cache.client.close()


# -------------- application --------------
def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        contact=settings.CONTACT,
        license_info=settings.CONTACT
    )

    application.include_router(router)
    application.add_event_handler("startup", create_tables)
    application.add_event_handler("startup", create_redis_cache_pool)
    application.add_event_handler("shutdown", close_redis_cache_pool)

    return application


app = create_application()
