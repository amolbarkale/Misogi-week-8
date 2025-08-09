from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from schemas import (
    MenuItemResponse,
    MenuItemUpdate,
    MenuItemWithRestaurant
)
from database import get_db
import crud

router = APIRouter(prefix= "/menu-items", tags=[""])

@router.get(
    "/",
    response_model=List[MenuItemResponse]
)
async def read_all_menu_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_all_menu_items(db, skip, limit)

@router.get(
    "/search",
    response_model=List[MenuItemResponse]
)
async def search_menu_items(
    category: Optional[str] = None,
    vegetarian: Optional[bool] = None,
    vegan: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await crud.search_menu_items(db, category, vegetarian, vegan, skip, limit)

@router.get(
    "/{item_id}",
    response_model=MenuItemResponse
)
async def read_menu_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    item = await crud.get_menu_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@router.get(
    "/{item_id}/with-restaurant",
    response_model=MenuItemWithRestaurant
)
async def read_menu_item_with_restaurant(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    item = await crud.get_menu_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@router.put(
    "/{item_id}",
    response_model=MenuItemResponse
)
async def update_menu_item_endpoint(
    item_id: int,
    payload: MenuItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated = await crud.update_menu_item(db, item_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return updated

@router.delete(
    "/{item_id}",
    response_model=MenuItemResponse
)
async def delete_menu_item_endpoint(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await crud.delete_menu_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return deleted
