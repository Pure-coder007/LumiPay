from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    # Call DRF’s default exception handler first
    response = exception_handler(exc, context)

    # If it's a throttle error, replace the message
    if isinstance(exc, Throttled):
        response = Response(
            {"message": "Too many requests. Please slow down."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    return response
