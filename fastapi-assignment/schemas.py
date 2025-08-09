from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time
from decimal import Decimal

# steps ->
# base
# create
# update
# response

class RestaurantBase():
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    cuisine_type: str = Field(..., min_length=2, max_length=50)
    address: str = Field(..., min_length=5, max_length=200)
    phone_number: str = Field(
        ...,
        pattern=r"^\+?[0-9\- ]{7,20}$",
        description="Phone number with country code, digits, dashes or spaces"
    )
    rating: float = Field(0.0, ge=0.0, le=5.0)
    is_active: bool = True
    opening_time: time
    closing_time: time

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    cuisine_type: Optional[str] = Field(None, min_length=2, max_length=50)
    address: Optional[str] = Field(None, min_length=5, max_length=200)
    phone_number: Optional[str] = Field(
        None,
        pattern=r"^\+?[0-9\- ]{7,20}$",
        description="Phone number with country code, digits, dashes or spaces"
    )
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    is_active: Optional[bool] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None

class RestaurantResponse(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    price: Decimal = Field(
        ...,
        gt=0,
        description="Positive price, two decimal places"
    )
    category: str = Field(..., min_length=2, max_length=50)
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_available: bool = True
    preparation_time: int = Field(
        ...,
        gt=0,
        description="Preparation time in minutes"
    )

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_available: Optional[bool] = None
    preparation_time: Optional[int] = Field(None, gt=0)

class MenuItemResponse(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RestaurantWithMenu(RestaurantResponse):
    menu_items: List[MenuItemResponse]

    class Config:
        from_attributes = True

class MenuItemWithRestaurant(MenuItemResponse):
    restaurant: RestaurantResponse

    class Config:
        from_attributes = True
