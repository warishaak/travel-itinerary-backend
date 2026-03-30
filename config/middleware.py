from uuid import uuid4

from config.request_context import set_request_id


class CorrelationIdMiddleware:
    """Attach a correlation id to each request/response and log context."""

    HEADER_NAME = "HTTP_X_REQUEST_ID"
    RESPONSE_HEADER = "X-Request-ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.META.get(self.HEADER_NAME) or str(uuid4())
        request.correlation_id = request_id
        set_request_id(request_id)

        response = self.get_response(request)
        response[self.RESPONSE_HEADER] = request_id
        return response
