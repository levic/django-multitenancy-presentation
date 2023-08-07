# from django.apps import apps
# from django.core import checks
# from django.core.checks.registry import registry
from django.core.management.base import BaseCommand
from django.db import transaction
from factory.fuzzy import FuzzyInteger
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
            default=30,
            help="Max number of projects to create per account",
        )

        parser.add_argument(
            "--min-tasks", action="store", type=int, default=0, help="Min number of tasks to create per project"
        )
        parser.add_argument(
            "--max-tasks", action="store", type=int, default=10, help="Max number of tasks to create per project"
        )

        parser.add_argument(
            "--min-subtasks", action="store", type=int, default=0, help="Min number of subtasks to create per task"
        )
        parser.add_argument(
            "--max-subtasks", action="store", type=int, default=10, help="Max number of subtasks to create per task"
        )

        parser.add_argument(
            "--rollback", action="store_true", help="Rollback (don't commit) database changes. Useful for testing"
        )

    @transaction.atomic
    def handle(
        self,
        *args,
        accounts: int,
        min_users: int,
        max_users: int,
        min_projects: int,
        max_projects: int,
        min_tasks: int,
        max_tasks: int,
        min_subtasks: int,
        max_subtasks: int,
        rollback: bool,
        **options,
    ):
        # make this deterministic
        reseed_random(0)

        accounts_count = 0
        users_count = 0
        projects_count = 0
        tasks_count = 0
        subtasks_count = 0

        for account_i in range(accounts):
            account = AccountFactory()
            accounts_count += 1

            n_users = FuzzyInteger(min_users, max_users).fuzz()
            users = UserFactory.create_batch(n_users, account=account, password="password")
            users_count += len(users)

            n_projects = FuzzyInteger(min_projects, max_projects).fuzz()
            projects = ProjectFactory.create_batch(n_projects, account=account)
            projects_count += len(projects)

            n_tasks = FuzzyInteger(min_tasks, max_tasks).fuzz() * len(projects)
            tasks = TaskFactory.create_batch(n_tasks, project=projects)
            tasks_count += len(tasks)

            n_subtasks = FuzzyInteger(min_subtasks, max_subtasks).fuzz() * len(tasks)
            subtasks = SubtaskFactory.create_batch(n_subtasks, task=tasks)
            subtasks_count += len(subtasks)

            if accounts > 10:
                print(".", end="", flush=True)
            else:
                print(account.slug, account.name)

        print()
        print(f"Accounts: {accounts_count}")
        print(f"Users: {users_count}")
        print(f"Projects: {projects_count}")
        print(f"Tasks: {tasks_count}")
        print(f"Subtasks: {subtasks_count}")

        if rollback:
            transaction.set_rollback(True)
