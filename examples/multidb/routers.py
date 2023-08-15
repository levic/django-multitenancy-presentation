from contextlib import contextmanager

from .middleware import get_current_tenancy_slug
from .middleware import use_current_tenancy_slug


class MultiDbTenancyRouter:
    """
    A router to direct database all operations to whatever the middleware
    thinks is the current database
    """

    def db_for_read(self, model, **hints):
        slug = get_current_tenancy_slug()
        print(f"- read from {slug}")
        return slug

    def db_for_write(self, model, **hints):
        slug = get_current_tenancy_slug()
        print(f"- write to {slug}")
        return slug

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True


@contextmanager
def use_tenancy_db(slug: str):
    with use_current_tenancy_slug(slug):
        yield
