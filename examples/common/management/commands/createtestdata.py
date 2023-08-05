# from django.apps import apps
# from django.core import checks
# from django.core.checks.registry import registry
from django.core.management.base import BaseCommand
from django.db import transaction
from factory.random import reseed_random

from ...factories import AccountFactory
from ...factories import UserFactory
from ...factories import ProjectFactory
from ...factories import TaskFactory
from ...factories import SubtaskFactory


class Command(BaseCommand):
    help = "Checks the entire Django project for potential problems."

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("--accounts", action="store", type=int, default=1, help="Number of accounts to create")

        parser.add_argument(
            "--min-users", action="store", type=int, default=1, help="Min number of users to create per account"
        )
        parser.add_argument(
            "--max-users", action="store", type=int, default=5, help="Max number of users to create per account"
        )

        parser.add_argument(
            "--min-projects", action="store", type=int, default=1, help="Min number of projects to create per account"
        )
        parser.add_argument(
            "--max-projects",
            action="store",
            type=int,
            default=50,
            help="Max number of projects to create per account",
        )

        parser.add_argument(
            "--min-tasks", action="store", type=int, default=3, help="Min number of tasks to create per project"
        )
        parser.add_argument(
            "--max-tasks", action="store", type=int, default=100, help="Max number of tasks to create per project"
        )

        parser.add_argument(
            "--min-subtasks", action="store", type=int, default=0, help="Min number of subtasks to create per task"
        )
        parser.add_argument(
            "--max-subtasks", action="store", type=int, default=5, help="Max number of subtasks to create per task"
        )

    @transaction.atomic
    def handle(
        self,
        *args,
        accounts,
        min_users,
        max_users,
        min_projects,
        max_projects,
        min_tasks,
        max_tasks,
        min_subtasks,
        max_subtasks,
        **options
    ):
        # make this deterministic
        reseed_random(0)

        for account_i in range(accounts):
            account = AccountFactory()

            for user_i in range(min_users, max_users+1):
                user = UserFactory(account=account, password="password")
                print(user.email)

        transaction.set_rollback(True)