from celery import Celery

celery_app = Celery(
    "zomato_v2",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,

    # reliability / control
    task_track_started=True,
    task_time_limit=300,        # hard kill after 5 minutes
    task_soft_time_limit=240,   # soft timeout; gives chance to clean up
    task_acks_late=True,        # redeliver if worker dies mid-task
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)