from contextlib import contextmanager

from django.db import connection
from django.db import transaction
from django.db.utils import ProgrammingError
import functools


from common.middleware import CurrentTenantMiddleware
from singleschema import models


class SingleSchemaMiddleware(CurrentTenantMiddleware):
    @classmethod
    def validate_current_tenant(cls, slug: str):
        # this is not strictly needed but is a sanity check to flag DB
        # connections that are not being cleaned up correctly
        # TODO: double check SQL error in a transaction

        # sanity check: check that the tenant ID isn't already set
        cursor = connection.cursor()
        cursor.execute("SELECT CURRENT_SETTING('django.tenant_id', TRUE);")
        current_slug = cursor.fetchone()[0]
        if current_slug is None:
            current_slug = ""

        if current_slug != slug:
            # if this happens then you probably have multiple requests sharing a connection
            raise Exception("django.tenant_id has been modified")

    @classmethod
    @contextmanager
    def use_current_tenancy(cls, slug: str):
        with super().use_current_tenancy_slug(slug):
            cls.validate_current_tenant("")

            tenant_id = tenant_id_from_slug(slug)

            cursor = connection.cursor()
            cursor.execute("SELECT SET_CONFIG('django.tenant_id', %s, false);", [tenant_id])

            try:
                yield

                cls.validate_current_tenant(tenant_id)

            finally:
                cursor.execute("SELECT SET_CONFIG('django.tenant_id', %s, false);", [""])


def current_tenant_id() -> int | None:
    slug = SingleSchemaMiddleware.get_current_tenancy_slug()
    return tenant_id_from_slug(slug) if slug is not None else None


@functools.cache
def tenant_id_from_slug(slug) -> int:
    """
    This assumes that account slugs are immutable and not reused
    so that it is fine to cache results

    If you had a *huge* number of tenants then you might want to instead cache this
    in thread-local storage (if you're happy for an extra query for every request)
    """
    results = models.Account.all_tenants.filter(slug=slug).values("id")
    assert len(results) == 1
    account_id = results[0]["id"]
    return account_id
