import common.models as common_models
from django.db.models import ForeignKey
from django.db.models import RESTRICT


class Account(common_models.Account):
    pass


class User(common_models.User):
    account = ForeignKey(Account, on_delete=RESTRICT)


class Project(common_models.Project):
    account = ForeignKey(Account, on_delete=RESTRICT)


class Task(common_models.Task):
    project = ForeignKey(Project, on_delete=RESTRICT)


class Subtask(common_models.Subtask):
    task = ForeignKey(Task, on_delete=RESTRICT)
