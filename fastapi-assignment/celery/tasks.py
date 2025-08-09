import asyncio
from decimal import Decimal
from typing import Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from celery_app import celery_app

DATABASE_URL = "sqlite+aiosqlite:///./test.db"


# Create our own engine/session for the worker process
engine = create_async_engine(DATABASE_URL, future=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@celery_app.task(
    bind=True,
    name="analytics.recompute_restaurant_stats",
    autoretry_for=(Exception,),
    retry_backoff=True,           # exponential backoff
    max_retries=5,
)
def recompute_restaurant_stats(self, restaurant_id: int) -> Dict[str, Any]:
    """
    Compute analytics for a single restaurant:
      - average menu price
      - total item count

    Celery task is sync, our DB is async -> wrap in asyncio.run
    """
    async def run():
        # Delay import to avoid circulars and only load ORM when needed
        from models import MenuItems
        async with SessionLocal() as db:
            avg_price = await db.scalar(
                select(func.avg(MenuItems.price)).where(MenuItems.restaurant_id == restaurant_id)
            )
            total_items = await db.scalar(
                select(func.count(MenuItems.id)).where(MenuItems.restaurant_id == restaurant_id)
            )

            # Convert Decimal/None to JSON-friendly
            avg_price_val = float(avg_price) if isinstance(avg_price, Decimal) else float(avg_price or 0)
            return {
                "restaurant_id": restaurant_id,
                "avg_price": avg_price_val,
                "total_items": int(total_items or 0),
            }

    return asyncio.run(run())
