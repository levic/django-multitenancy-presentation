# from django.apps import apps
from contextlib import nullcontext

from django.conf import settings

# from django.core import checks
# from django.core.checks.registry import registry
from django.core.management.base import BaseCommand
from django.db import transaction
from factory.fuzzy import FuzzyInteger
from factory.random import reseed_random

from multidb.routers import use_tenancy_db
from ...factories import AccountFactory
from ...factories import UserFactory
from ...factories import ProjectFactory
from ...factories import TaskFactory
from ...factories import SubtaskFactory


class Command(BaseCommand):
    help = "Checks the entire Django project for potential problems."

    requires_system_checks = []

    def add_arguments(self, parser):
        try:
            default_accounts = settings.MULTIDB_COUNT
        except AttributeError:
            default_accounts = 1

        parser.add_argument(
            "--accounts",
            action="store",
            type=int,
            default=default_accounts,
            help="Number of accounts to create (default %(default)s)",
        )

        parser.add_argument(
            "--min-users",
            action="store",
            type=int,
            default=1,
            help="Min average number of users to create per account",
        )
        parser.add_argument(
            "--max-users",
            action="store",
            type=int,
            default=5,
            help="Max average number of users to create per account",
        )

        parser.add_argument(
            "--min-projects",
            action="store",
            type=int,
            default=1,
            help="Min average number of projects to create per account",
        )
        parser.add_argument(
            "--max-projects",
            action="store",
            type=int,
            default=30,
            help="Max number of projects to create per account",
        )

        parser.add_argument(
            "--min-tasks",
            action="store",
            type=int,
            default=1,
            help="Min average number of tasks to create per project",
        )
        parser.add_argument(
            "--max-tasks",
            action="store",
            type=int,
            default=10,
            help="Max average number of tasks to create per project",
        )

        parser.add_argument(
            "--min-subtasks",
            action="store",
            type=int,
            default=1,
            help="Min average number of subtasks to create per task",
        )
        parser.add_argument(
            "--max-subtasks",
            action="store",
            type=int,
            default=10,
            help="Max average number of subtasks to create per task",
        )

        parser.add_argument(
            "--rollback", action="store_true", help="Rollback (don't commit) database changes. Useful for testing"
        )

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

        if hasattr(settings, "MULTIDB_COUNT"):
            assert accounts <= settings.MULTIDB_COUNT

            # the MultiDB setup requires you to do some manual DB switching for each account
            # (esp transactions)
            # in particular, on a production site you'll want to create your own wrapper to transaction.atomic()
            def account_context(account_slug):
                return use_tenancy_db(account_slug)

            def get_db_alias(account_slug):
                return account_slug

        else:
            account_context = nullcontext

            def get_db_alias(account_slug):
                return "default"

        for account_i in range(accounts):
            account_slug = f"tenant-{account_i}"
            db_alias = get_db_alias(account_slug)
            with account_context(account_slug):
                with transaction.atomic(using=db_alias):
                    account = AccountFactory(slug=account_slug)
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

                    if rollback:
                        transaction.set_rollback(True, using=db_alias)

        print()
        print(f"Accounts: {accounts_count}")
        print(f"Users: {users_count}")
        print(f"Projects: {projects_count}")
        print(f"Tasks: {tasks_count}")
        print(f"Subtasks: {subtasks_count}")
