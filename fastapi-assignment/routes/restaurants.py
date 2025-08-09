from fastapi import FastAPI, APIRouter, status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas import (
    RestaurantBase,
    RestaurantCreate,
    RestaurantResponse,
    RestaurantUpdate,
    MenuItemBase,
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate
)
from database import get_db
import crud

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(payload: RestaurantCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_restaurant(db, payload)

@router.get("/", response_model=List[RestaurantResponse])
async def read_restaurants(skip:int = 0, limit:int =  10, db: AsyncSession = Depends(get_db)):
    return await crud.get_restaurants(db, skip, limit)

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def read_restaurant(
restaurant_id: int,
db: AsyncSession = Depends(get_db)
):
    restaurnt = await crud.get_restaurant(db, restaurant_id)
    if not restaurnt:
        raise HTTPException(status_code=404, detail="restaurant not found")

@router.put("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(restaurant_id: int, payload:RestaurantUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_restaurant(db, restaurant_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return updated

@router.delete("/{restaurant_id}", response_model=RestaurantResponse)
async def delete_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    restaurant = await crud.delete_restaurant(restaurant_id, db)
    if not restaurant:
        raise HTTPException(status_code=404, detail="restaurant not found")
    return restaurant

@router.post("/{restaurant_id}/menu-items", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item_for_restaurant(
    restaurant_id: int,
    payload: MenuItemCreate,
    db: AsyncSession = Depends(get_db)
):
    restaurant = await crud.create_menu_item_for_restaurant(restaurant_id, payload, db)
    if not restaurant:
        raise HTTPException(status_code=404, detail="restaurnat no found")
    return restaurant

@router.get("/{restaurant_id}/menu", response_model=List[MenuItemResponse])
async def read_menu_for_restaurant(restaurant_id: int, skip: int = 0, limit: int = 50, db: AsyncSession = Depends[get_db]):
    menu = await crud.read_menu_for_restaurant(restaurant_id, db)
    if not menu:
        HTTPException(status_code=404, detail="Menu for the restaurnat not found")
    return menu