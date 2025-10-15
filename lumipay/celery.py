import os
from celery import Celery

# set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "educore.settings")

app = Celery("lumipay")

# Using Redis as the broker
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs
app.autodiscover_tasks()
