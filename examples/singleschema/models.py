import common.models as common_models
from django.db.models import ForeignKey
from django.db.models import RESTRICT

from .managers import TenantedManager


class Account(common_models.Account):
    objects = TenantedManager(require_tenant=True)
    all_tenants = TenantedManager(require_tenant=False)

    class Meta:
        base_manager_name = "all_tenants"


class User(common_models.User):
    account = ForeignKey(Account, on_delete=RESTRICT)

    objects = TenantedManager(require_tenant=True)
    all_tenants = TenantedManager(require_tenant=False)

    class Meta:
        base_manager_name = "all_tenants"


class Project(common_models.Project):
    account = ForeignKey(Account, on_delete=RESTRICT)

    objects = TenantedManager(require_tenant=True)
    all_tenants = TenantedManager(require_tenant=False)

    class Meta:
        base_manager_name = "all_tenants"


class Task(common_models.Task):
    account = ForeignKey(Account, on_delete=RESTRICT)
    project = ForeignKey(Project, on_delete=RESTRICT)

    objects = TenantedManager(require_tenant=True)
    all_tenants = TenantedManager(require_tenant=False)

    class Meta:
        base_manager_name = "all_tenants"


class Subtask(common_models.Subtask):
    account = ForeignKey(Account, on_delete=RESTRICT)
    task = ForeignKey(Task, on_delete=RESTRICT)

    objects = TenantedManager(require_tenant=True)
    all_tenants = TenantedManager(require_tenant=False)

    class Meta:
        base_manager_name = "all_tenants"
