from common.views import BaseSubtaskListView
from singleschema.middleware import current_tenant_id


class FilterTenantMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter_tenant(current_tenant_id())


class SubtaskListView(FilterTenantMixin, BaseSubtaskListView):
    pass
