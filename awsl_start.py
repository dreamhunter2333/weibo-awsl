import logging

from celery import Celery
from celery.schedules import crontab

from awsl.awsl import WbAwsl
from awsl.config import settings


logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(name)s: %(message)s",
    level=logging.INFO
)

app = Celery('awsl-tasks', broker=settings.broker)


@app.task
def start_awsl():
    WbAwsl.start()


app.conf.beat_schedule = {
    "awsl-tasks": {
        "task": "awsl_start.start_awsl",
        "schedule": crontab(hour="*", minute=1)
    }
}
