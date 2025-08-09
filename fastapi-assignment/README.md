# Zomato — FastAPI · Async SQLAlchemy · Celery

A clean FastAPI project that manages **Restaurants** and **Menu Items**, plus a focused **Celery** integration for asynchronous analytics (average menu price & item count). This README covers **setup, configuration, routes, and Celery workflow**—no fluff.

---

## Table of Contents

* [Overview](#overview)
* [Tech Stack](#tech-stack)
* [Project Layout](#project-layout)
* [Prerequisites](#prerequisites)
* [Configuration](#configuration)
* [Installation](#installation)
* [Running Locally](#running-locally)

  * [1) Start Redis](#1-start-redis)
  * [2) Start the API](#2-start-the-api)
  * [3) Start the Celery Worker](#3-start-the-celery-worker)
* [API Routes](#api-routes)

  * [Restaurants](#restaurants)
  * [Menu Items](#menu-items)
  * [Analytics (Celery)](#analytics-celery)
* [Examples](#examples)

  * [Create a Restaurant](#create-a-restaurant)
  * [Create a Menu Item under a Restaurant](#create-a-menu-item-under-a-restaurant)
  * [Get Restaurant With Full Menu](#get-restaurant-with-full-menu)
  * [Enqueue Analytics Task](#enqueue-analytics-task)
  * [Check Task Status](#check-task-status)
* [How Celery Fits Here](#how-celery-fits-here)
* [Internals & Conventions](#internals--conventions)
* [Troubleshooting](#troubleshooting)
* [Next Steps](#next-steps)

---

## Overview

This project demonstrates a realistic FastAPI setup with:

* Async CRUD for **Restaurants** and **Menu Items** (SQLAlchemy 2.x).
* Pydantic v2 schemas with `from_attributes=True` for clean ORM → JSON serialization.
* A minimal but production-style **Celery** task to compute restaurant analytics:

  * **average menu price**
  * **total item count**

The Celery piece is intentionally small—useful for learning without overcomplicating the app.

---

## Tech Stack

* **API**: FastAPI (async)
* **ORM/DB**: SQLAlchemy 2.x (async) + SQLite (`aiosqlite` driver)
* **Validation**: Pydantic v2
* **Background jobs**: Celery (Redis as broker & result backend)
* **Server**: Uvicorn

---

## Project Layout

```
.
├── main.py
├── database.py
├── models.py
├── schemas.py
├── crud.py                 # optional service layer (some routes call it)
├── routes/
│   ├── restaurants.py
│   └── menu_items.py
├── celery/
│   ├── celery_app.py # Celery app configuration
│   └── tasks.py  # Celery tasks (analytics)            
└── requirements.txt
```

---

## Prerequisites

* Python **3.10+**
* **Redis** (quickest via Docker)
* (Optional) `curl` for quick testing

---

## Configuration

Defaults used by the code:

* **Database**:
  `DATABASE_URL=sqlite+aiosqlite:///./test.db`

* **Celery Broker & Result Backend** (Redis):
  `REDIS_BROKER_URL=redis://localhost:6379/0`
  `REDIS_RESULT_BACKEND=redis://localhost:6379/1`

You can also define a `.env` and load it in your modules if you prefer:

```env
DATABASE_URL=sqlite+aiosqlite:///./restaurants.db
REDIS_BROKER_URL=redis://localhost:6379/0
REDIS_RESULT_BACKEND=redis://localhost:6379/1
```

> Note: If you switch to Postgres later, install `asyncpg`, update `DATABASE_URL`, and adjust your engine creation.

---

## Installation

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# With requirements.txt
pip install -r requirements.txt

# Or minimal install
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic celery[redis] redis
```

---

## Running Locally

### 1) Start Redis

**Fastest (any OS via Docker):**

```bash
docker run --name redis -p 6379:6379 -d redis:7-alpine
docker exec -it redis redis-cli ping   # -> PONG
```

### 2) Start the API

```bash
uvicorn main:app --reload
# API:  http://127.0.0.1:8000
# Docs: http://127.0.0.1:8000/docs
```

> On startup, the app calls a helper to create missing tables (dev-friendly). For production, prefer Alembic migrations.

### 3) Start the Celery Worker

```bash
# macOS/Linux
celery -A celery_app.celery_app worker -l info

# Windows (use the solo pool)
celery -A celery_app.celery_app worker -l info -P solo
```

---

## API Routes

### Restaurants

| Method | Path                                      | Description                           |
| :----: | ----------------------------------------- | ------------------------------------- |
|  POST  | `/restaurants/`                           | Create restaurant                     |
|   GET  | `/restaurants/`                           | List restaurants                      |
|   GET  | `/restaurants/{restaurant_id}`            | Get one restaurant                    |
|   PUT  | `/restaurants/{restaurant_id}`            | Update restaurant (partial allowed)   |
| DELETE | `/restaurants/{restaurant_id}`            | Delete restaurant                     |
|   GET  | `/restaurants/{restaurant_id}/with-menu`  | Restaurant with all its menu items    |
|  POST  | `/restaurants/{restaurant_id}/menu-items` | Create a menu item for the restaurant |

### Menu Items

| Method | Path                                    | Description                             |
| :----: | --------------------------------------- | --------------------------------------- |
|   GET  | `/menu-items/`                          | List menu items                         |
|   GET  | `/menu-items/search`                    | Filter by category / vegetarian / vegan |
|   GET  | `/menu-items/{item_id}`                 | Get one menu item                       |
|   GET  | `/menu-items/{item_id}/with-restaurant` | Item with parent restaurant             |
|   PUT  | `/menu-items/{item_id}`                 | Update menu item                        |
| DELETE | `/menu-items/{item_id}`                 | Delete menu item                        |

### Analytics (Celery)

| Method | Path                                               | Description                                   |
| :----: | -------------------------------------------------- | --------------------------------------------- |
|  POST  | `/analytics/restaurants/{restaurant_id}/recompute` | Enqueue analytics job (avg price, item count) |
|   GET  | `/analytics/tasks/{task_id}`                       | Check Celery task status/result               |

---

## Examples

### Create a Restaurant

```bash
curl -X POST http://127.0.0.1:8000/restaurants/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pasta Palace",
    "description": "Homemade Italian cuisine",
    "cuisine_type": "Italian",
    "address": "123 Main St",
    "phone_number": "+1-555-123-4567",
    "rating": 4.5,
    "is_active": true,
    "opening_time": "10:00:00",
    "closing_time": "22:00:00"
  }'
```

### Create a Menu Item under a Restaurant

```bash
curl -X POST http://127.0.0.1:8000/restaurants/1/menu-items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Margherita Pizza",
    "description": "Tomato, mozzarella, basil",
    "price": 12.50,
    "category": "Pizza",
    "is_vegetarian": true,
    "is_vegan": false,
    "is_available": true,
    "preparation_time": 15
  }'
```

### Get Restaurant With Full Menu

```bash
curl http://127.0.0.1:8000/restaurants/1/with-menu
```

### Enqueue Analytics Task

```bash
curl -X POST http://127.0.0.1:8000/analytics/restaurants/1/recompute
# -> {"task_id":"<uuid>","state":"QUEUED"}
```

### Check Task Status

```bash
curl http://127.0.0.1:8000/analytics/tasks/<uuid>
# -> {"task_id":"<uuid>","state":"SUCCESS","result":{"restaurant_id":1,"avg_price":12.5,"total_items":6}}
```

---

## How Celery Fits Here

**Use case:** offload a small analytics computation so HTTP requests stay fast.

* **Task:** `recompute_restaurant_stats(restaurant_id)` computes:

  * `avg_price` across all `MenuItem.price` values for that restaurant
  * `total_items` count for that restaurant
* **Flow:** The API enqueues a task and returns a `task_id` immediately. A separate **Celery worker** computes the result and stores it in the Redis result backend. The client polls `GET /analytics/tasks/{task_id}` to retrieve the status/result.

This demonstrates **asynchronous background processing** with retries and independent scaling—without cluttering your core CRUD.

---

## Internals & Conventions

* **Async SQLAlchemy**: Use `AsyncSession`, `await db.execute(...)`, `await db.commit()`.
* **Pydantic v2**: Schemas use `from_attributes=True`, so returning ORM objects from endpoints is fine.
* **Startup DB creation**: `create_tables()` creates missing tables for development. In production, prefer **Alembic** migrations.
* **Error handling**: Endpoints return `404` when records are missing.
* **Dependencies**: `Depends(get_db)` injects an `AsyncSession` per request; sessions are cleaned up automatically.
* **Celery tasks**: Create a **new engine/session inside the task** (do not reuse FastAPI’s session), return JSON-serializable results.

---

## Troubleshooting

* **`redis-server: command not found`**
  Use the Docker command above to run Redis quickly, or install natively (brew/apt).

* **Windows Celery**
  Use the solo pool: `-P solo`.

* **Port 6379 already in use**
  Stop the conflicting service or map Redis to another port and update the URLs.

* **DB path mismatch**
  Ensure **both** the API and Celery worker point to the **same** `DATABASE_URL` so they see the same data.

* **Lazy relationship access fails**
  Make sure relationships are loaded while the session is open. You’re using `lazy="selectin"`, which is a sensible default.

---