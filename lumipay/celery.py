# import os
# from celery import Celery
#
# # set the default Django settings module
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumipay.settings")
#
# app = Celery("lumipay")
#
# # Using Redis as the broker and result backend
# app.conf.broker_url = 'redis://localhost:6379/0'
# app.conf.result_backend = 'redis://localhost:6379/0'
#
# # Configure periodic tasks (if needed)
# app.conf.beat_schedule = {}
#
# # Load task modules from all registered Django app configs
# app.autodiscover_tasks()
#
# # This allows you to schedule items in the Django admin.
# app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
#

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LumiPay.settings")

app = Celery("LumiPay")

# Use Redis as the broker (the messenger between Django and Celery)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all Django apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")



