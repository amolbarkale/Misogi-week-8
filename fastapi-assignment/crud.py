from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from decimal import Decimal
from models import Restaurant, MenuItems
from schemas import MenuItemCreate, MenuItemUpdate
from typing import List, Optional

async def create_menu_item(restaurant_id: int, payload:MenuItemCreate, db: AsyncSession)-> MenuItems:
    # ensure parent restaurant exists
    response = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    parent = response.scalar_one_or_none()
    if not parent:
        return None

    # create - save new menu item
    db_item = MenuItems(**payload.dict(), restaurant_id=restaurant_id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_menu_item(restaurant_id: int, skip: int, limit: int, db: AsyncSession):
    response = await db.execute(select(MenuItems).where(MenuItems.id == restaurant_id))

    return response.scalar_one_or_none()

async def get_all_menu_items(db: AsyncSession, skip: int, limit: int) -> List[MenuItems]:
    response = await db.execute(select(MenuItems).offset(skip).limit(limit))
    return response.scalars().all()



async def update_menu_item(
    db: AsyncSession,
    item_id: int,
    item_update: MenuItemUpdate
) -> Optional[MenuItems]:
    # Fetch existing
    res = await db.execute(select(MenuItems).where(MenuItems.id == item_id))
    db_item = res.scalar_one_or_none()
    if not db_item:
        return None

    # Apply changes
    update_data = item_update.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(db_item, field, val)

    await db.commit()
    await db.refresh(db_item)
    return db_item

async def delete_menu_item(
    db: AsyncSession,
    item_id: int
) -> Optional[MenuItems]:
    res = await db.execute(select(MenuItems).where(MenuItems.id == item_id))
    db_item = res.scalar_one_or_none()
    if not db_item:
        return None
    await db.delete(db_item)
    await db.commit()
    return db_item

async def search_menu_items(
    db: AsyncSession,
    category: Optional[str] = None,
    vegetarian: Optional[bool] = None,
    vegan: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[MenuItems]:
    # Build base query
    stmt = select(MenuItems)
    if category:
        stmt = stmt.where(MenuItems.category.ilike(f"%{category}%"))
    if vegetarian is not None:
        stmt = stmt.where(MenuItems.is_vegetarian == vegetarian)
    if vegan is not None:
        stmt = stmt.where(MenuItems.is_vegan == vegan)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_menu_for_restaurant(
    db: AsyncSession,
    restaurant_id: int
) -> List[MenuItems]:
    result = await db.execute(
        select(MenuItems)
        .where(MenuItems.restaurant_id == restaurant_id)
    )
    return result.scalars().all()

async def get_restaurant_with_menu(
    db: AsyncSession,
    restaurant_id: int
) -> Optional[Restaurant]:
    # Use selectinload to pull in menu_items efficiently
    result = await db.execute(
        select(Restaurant)
        .options(selectinload(Restaurant.menu_items))
        .where(Restaurant.id == restaurant_id)
    )
    return result.scalar_one_or_none()

