from django.utils.timezone import now
from authentication.models import AuditLog
from django.contrib.auth.middleware import get_user
import threading

# Use thread-local storage to prevent duplicate log entries
_thread_locals = threading.local()

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = get_user(request)
        if user.is_authenticated and not getattr(_thread_locals, "log_saved", False):
            action = f"{request.method} {request.path}"
            AuditLog.objects.create(user=user, action=action)
            _thread_locals.log_saved = True  # Prevent duplicate logs in the same request

        return response
