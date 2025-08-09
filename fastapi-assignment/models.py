from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Time,
    DateTime,
    Text,
    ForeignKey,
    Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    cuisine_type = Column(String(50), nullable=False, index=True)
    address = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True)
    rating = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # one-to-many relationship for menu_items
    menu_items = relationship(
        "MenuItems",
        back_populates="restaurants",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class MenuItems(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    preparation_time = Column(Integer, nullable=False)  # in minutes

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # many-to-one relationship for restaurants
    restaurant = relationship(
        "Restaurant",
        back_populates="menu_items",
        lazy="selectin"
    )