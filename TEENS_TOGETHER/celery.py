
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import logging
from celery.signals import setup_logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TEENS_TOGETHER.settings")

app = Celery("TEENS_TOGETHER")


app.config_from_object("django.conf:settings", namespace="CELERY")



@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig  
    from django.conf import settings 

    dictConfig(settings.LOGGING)


app.autodiscover_tasks()



@app.task(bind=True)
def debug_task():
    print(f"Request: {self.request!r}")
