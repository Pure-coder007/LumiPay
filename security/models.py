from django.db import models
from django.utils import timezone
from django.conf import settings


class ThrottleLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="throttle_logs",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    endpoint = models.CharField(max_length=255, db_index=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    user_agent = models.CharField(max_length=512, blank=True, null=True)
    attempts = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["ip_address", "endpoint"]),
            models.Index(fields=["timestamp"]),
        ]
        verbose_name = "Throttle Log"
        verbose_name_plural = "Throttle Logs"

    def __str__(self):
        return f"{self.ip_address or 'Anonymous'} tried {self.endpoint} at {self.timestamp:%Y-%m-%d %H:%M:%S}"
