import os
from celery import Celery

# set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumipay.settings")

app = Celery("lumipay")

# Using Redis as the broker and result backend
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

# Configure periodic tasks (if needed)
app.conf.beat_schedule = {}

# Load task modules from all registered Django app configs
app.autodiscover_tasks()

# This allows you to schedule items in the Django admin.
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
