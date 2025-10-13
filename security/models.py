from django.db import models
from django.utils import timezone
from django.conf import settings

class ThrottleLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    user_agent = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return f"{self.ip_address or 'Anonymous'} - {self.endpoint} - {self.timestamp}"

# Create your models here.
