from contextvars import ContextVar

_REQUEST_ID = ContextVar("request_id", default="-")


def set_request_id(request_id):
    _REQUEST_ID.set(request_id)


def get_request_id():
    return _REQUEST_ID.get()
