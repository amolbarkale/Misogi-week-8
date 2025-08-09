from fastapi import FastAPI
import uvicorn
from routes.restaurants import router as restaurants_router
from routes.menu_items import router as menu_items_router
from routes.analytics import router as analytics_router
from database import create_tables

app = FastAPI(title="food delivery application", description="description", version="0.1")

app.include_router(restaurants_router)
app.include_router(menu_items_router)
app.include_router(analytics_router)

@app.on_event("startup")
async def on_startup():
    await create_tables()

@app.get("/", tags=["root"])
async def read_root():
    return {"message": "Welcome to Zomato v2 API"}

if __name__ == "__main__":
    uvicorn("main:app", host="127.0.0.1", port=8000, reload=True)