import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class GlobalExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error(f"Error inesperado: {exception}")
        return JsonResponse(
            {"error": str(exception)},
            status=500
        )