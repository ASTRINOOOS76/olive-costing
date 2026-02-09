from celery import Celery

celery_app = Celery(
    "food_crm",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.task_routes = {
    "app.workers.tasks.imap_sync_task": {"queue": "email"},
    "app.workers.tasks.mydata_submit_task": {"queue": "invoicing"},
}

celery_app.conf.beat_schedule = {
    "imap-sync-every-5-min": {
        "task": "app.workers.tasks.imap_sync_task",
        "schedule": 300.0,  # every 5 minutes
        "args": [],
    },
}
