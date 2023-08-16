from contextlib import contextmanager

from multidb.middleware import MultiDbMiddleware


class MultiDbTenancyRouter:
    """
    A router to direct database all operations to whatever the middleware
    thinks is the current database
    """

    def db_for_read(self, model, **hints):
        slug = MultiDbMiddleware.get_current_tenancy_slug()
        return slug

    def db_for_write(self, model, **hints):
        slug = MultiDbMiddleware.get_current_tenancy_slug()
        return slug

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
