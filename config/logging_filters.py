import logging

from config.request_context import get_request_id


class RequestIDFilter(logging.Filter):
    """Inject correlation id into every log record."""

    def filter(self, record):
        record.request_id = get_request_id()
        return True
