from rest_framework.throttling import UserRateThrottle
from security.models import ThrottleLog
from django.utils import timezone

class LoginRateThrottle(UserRateThrottle):
    scope = "login"

    def throttle_failure(self):
        request = self.request
        user = getattr(request, "user", None)
        ip = self.get_ident(request)
        endpoint = request.path
        user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

        # Log the throttling event
        ThrottleLog.objects.create(
            user=user if user.is_authenticated else None,
            ip_address=ip,
            endpoint=endpoint,
            user_agent=user_agent,
            timestamp=timezone.now(),
        )
        return super().throttle_failure()
