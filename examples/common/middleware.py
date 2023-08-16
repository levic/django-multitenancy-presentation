from collections.abc import Callable
from contextlib import contextmanager
import threading

from django.http import HttpRequest
from django.http import HttpResponse
import re

_threadlocal_storage = threading.local()


class CurrentTenantMiddleware:
    get_response: Callable[[HttpRequest], HttpResponse]

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        tenancy_slug = self.get_tenancy_slug_from_request(request)

        # the type(self) is needed because chaining classmethod+contextmanager
        # causes issues when calling with self.some_class_method()
        context = type(self).use_current_tenancy_slug(tenancy_slug)

        with context:
            response = self.get_response(request)
            return response

    def get_tenancy_slug_from_request(self, request: HttpRequest) -> str:
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

    @classmethod
    @contextmanager
    def use_current_tenancy_slug(cls, slug: str):
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

    @classmethod
    def get_current_tenancy_slug(cls) -> str:
        return _threadlocal_storage.tenancy_slug
