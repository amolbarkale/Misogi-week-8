from fastapi import APIRouter
from celery.celery_app import celery_app
from celery.tasks import recompute_restaurant_stats

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/restaurants/{restaurant_id}/recompute")
async def kick_stats(restaurant_id: int):
    """
    Enqueue the task and return a task id immediately.
    """
    task = recompute_restaurant_stats.delay(restaurant_id)
    return {"task_id": task.id, "state": "QUEUED"}

@router.get("/tasks/{task_id}")
async def task_status(task_id: str):
    """
    Poll task status/result.
    """
    res = celery_app.AsyncResult(task_id)
    body = {"task_id": task_id, "state": res.state}
    if res.successful():
        body["result"] = res.result
    elif res.failed():
        body["error"] = str(res.info)
    return body
