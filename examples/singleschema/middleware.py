import functools


from common.middleware import CurrentTenantMiddleware
from singleschema.models import Account


class SingleSchemaMiddleware(CurrentTenantMiddleware):
    pass


def current_tenant_id() -> int:
    return tenant_id_from_slug(SingleSchemaMiddleware.get_current_tenancy_slug())


@functools.cache
def tenant_id_from_slug(slug) -> int:
    """
    This assumes that account slugs are immutable and not reused
    so that it is fine to cache results

    If you had a *huge* number of tenants then you might want to instead cache this
    in thread-local storage (if you're happy for an extra query for every request)
    """
    results = Account.all_tenants.filter(slug=slug).values("id")
    assert len(results) == 1
    account_id = results[0]["id"]
    return account_id
