from collections.abc import Callable
from contextlib import contextmanager
import threading

from django.http import HttpRequest
from django.http import HttpResponse
import re

_threadlocal_storage = threading.local()


class MultiDbMiddleware:
    get_response: Callable[[HttpRequest], HttpResponse]

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        tenancy_slug = get_tenancy_slug_from_request(request)
        with use_current_tenancy_slug(tenancy_slug):
            response = self.get_response(request)
            return response


def get_tenancy_slug_from_request(request: HttpRequest) -> str:
    # adapt this to whatever scheme you use for determining the tenancy
    #
    # this code assumes that the domains look like:
    #  tenancy-0.localhost
    #  tenancy-1.localhost
    #  tenancy-2.localhost
    # etc
    host = request.get_host()

    if match := re.fullmatch("^(?P<tenant>tenant-[0-9]+)\.localhost(:[0-9]+)?", host):
        return match["tenant"]

    raise ValueError("Unsupported hostname")


@contextmanager
def use_current_tenancy_slug(slug: str):
    # this code is not designed to be reentrant
    # (it could be adapted to use a stack though)
    assert not hasattr(_threadlocal_storage, "tenancy_slug")

    _threadlocal_storage.tenancy_slug = slug

    try:
        yield

        # sanity check
        assert _threadlocal_storage.tenancy_slug == slug

    finally:
        del _threadlocal_storage.tenancy_slug


def get_current_tenancy_slug() -> str:
    return _threadlocal_storage.tenancy_slug
