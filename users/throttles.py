from rest_framework.throttling import UserRateThrottle
from django.utils import timezone
from security.models import ThrottleLog


class LoginRateThrottle(UserRateThrottle):
    scope = "login"

    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)
        if not allowed:
            self.log_throttled_request(request)
        return allowed

    def log_throttled_request(self, request):
        user = getattr(request, "user", None)
        ip = self.get_ident(request)
        endpoint = request.path
        user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

        ThrottleLog.objects.create(
            user=user if user and user.is_authenticated else None,
            ip_address=ip,
            endpoint=endpoint,
            user_agent=user_agent,
            timestamp=timezone.now(),
        )
