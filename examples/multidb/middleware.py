from common.middleware import CurrentTenantMiddleware


class MultiDbMiddleware(CurrentTenantMiddleware):
    # there's nothing special that needs to happen here beyond the base class:
    # it's the DB router that will call back to the middleware to check the current tenant
    pass
