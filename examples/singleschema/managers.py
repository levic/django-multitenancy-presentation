"""
Helper base classes for managers & querysets

In a production system you may also want to:
- split the QuerySet/Manager into Mixins so that you don't end up with
  diamond inheritance with metaclasses
- add extra system checks on the models to check that they use all use these classes
"""
from typing import Self

from django.db.models import Manager
from django.db.models import QuerySet


class TenantMissingError(RuntimeError):
    """
    Tried to run a query on a tenanted model but didn't call .filter_scope() or .set_require_tenant(False)
    """

    pass


class TenantedQuerySet(QuerySet):
    # (The reason for the slightly different code layout here is to match the upstream QuerySet code)

    _require_tenant: bool
    _is_filter_tenant_applied: int

    ########################
    # PYTHON MAGIC METHODS #
    ########################

    def __init__(self, *args, **kwargs):
        self._require_tenant = True
        self._is_filter_tenant_applied = False
        super().__init__(*args, **kwargs)

    def __iter__(self):
        self._validate_filter_tenant_applied()
        return super().__iter__()

    ####################################
    # METHODS THAT DO DATABASE QUERIES #
    ####################################

    def iterator(self):
        self._validate_filter_tenant_applied()
        return super().iterator()

    def count(self):
        self._validate_filter_tenant_applied()
        return super().count()

    ##################################################
    # PUBLIC METHODS THAT RETURN A QUERYSET SUBCLASS #
    ##################################################

    def values_list(self, *fields, **kwargs):
        self._validate_filter_tenant_applied()
        return super().values_list(*fields, **kwargs)

    ##################################################################
    # PUBLIC METHODS THAT ALTER ATTRIBUTES AND RETURN A NEW QUERYSET #
    ##################################################################

    def union(self, *other_qs, **kwargs):
        self._validate_filter_tenant_applied()
        for qs in other_qs:
            if isinstance(qs, TenantedQuerySet):
                qs._validate_filter_tenant_applied()
        return super().union(*other_qs, **kwargs)

    def intersection(self, *other_qs):
        self._validate_filter_tenant_applied()
        for qs in other_qs:
            if isinstance(qs, TenantedQuerySet):
                qs._enforce_scopes()
        return super().intersection(*other_qs)

    def extra(self, **kwargs):
        raise NotImplementedError("extra() is deprecated in Django")

    ###################
    # PRIVATE METHODS #
    ###################

    def _clone(self, **kwargs):
        clone = super()._clone(**kwargs)
        if "_require_tenant" not in kwargs:
            clone._require_tenant = self._require_tenant
        if "_is_filter_tenant_applied" not in kwargs:
            clone._is_filter_tenant_applied = self._is_filter_tenant_applied
        return clone

    def _fetch_all(self):
        self._validate_filter_tenant_applied()
        return super()._fetch_all()

    # --------------------------
    # New ScopedQuerySet methods

    def _validate_filter_tenant_applied(self):
        if self._require_tenant and not self._is_filter_tenant_applied:
            msg = f"Attempt to query {self.model.__name__} without applying a tenant"
            raise TenantMissingError(msg)

    def filter_tenant(self, account) -> Self:
        self._is_filter_tenant_applied = True
        return self.filter(account=account)

    def set_require_tenant(self, value: bool = True) -> Self:
        self._require_tenant = value
        return self


class TenantedManager(Manager):
    _queryset_class: QuerySet = TenantedQuerySet
    _require_tenant: bool

    def __init__(self, *args, require_tenant: bool = True, **kwargs):
        """
        Note that RelatedManager and ManyRelatedManager will create a new copy of this manager and
        won't include any custom parameters so they must all be optional
        """
        super().__init__(*args, **kwargs)
        self._require_tenant = require_tenant

    def get_queryset(self) -> TenantedQuerySet:
        qs = super().get_queryset()
        qs = qs.set_require_tenant(self._require_tenant)

        if not isinstance(qs, TenantedQuerySet):
            # make sure that a dev didn't override the queryset
            # and forget to include the scoping mechanism(s)
            raise RuntimeError("TenantedManager.get_queryset() should return a TenantedQuerySet")

        return qs
