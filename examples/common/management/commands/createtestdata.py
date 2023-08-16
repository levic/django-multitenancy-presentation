import importlib

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import router
from django.db import transaction
from factory.fuzzy import FuzzyInteger
from factory.random import reseed_random

from multidb.middleware import MultiDbMiddleware
from singleschema.middleware import SingleSchemaMiddleware
from ...factories import AccountFactory
from ...factories import UserFactory
from ...factories import ProjectFactory
from ...factories import TaskFactory
from ...factories import SubtaskFactory

models = importlib.import_module(settings.MODELS_MODULE + ".models")


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

        if "multidb" in settings.INSTALLED_APPS:
            assert accounts <= settings.MULTIDB_COUNT
            account_context = MultiDbMiddleware.use_current_tenancy_slug
        elif "singleschema":
            account_context = SingleSchemaMiddleware.use_current_tenancy_slug
        else:
            raise RuntimeError("Unrecognised configuration")

        for account_i in range(accounts):
            account_slug = f"tenant-{account_i}"
            with account_context(account_slug):
                account = AccountFactory.build(slug=account_slug)
                db_alias = router.db_for_write(models.Account, instance=account)
                with transaction.atomic(using=db_alias):
                    account.save()
                    accounts_count += 1

                    n_users = FuzzyInteger(min_users, max_users).fuzz()
                    users = UserFactory.create_batch(n_users, account=account, password="password")
                    users_count += len(users)

                    n_projects = FuzzyInteger(min_projects, max_projects).fuzz()
                    projects = ProjectFactory.create_batch(n_projects, account=account)
                    projects_count += len(projects)

                    n_tasks = FuzzyInteger(min_tasks, max_tasks).fuzz() * len(projects)
                    tasks = TaskFactory.create_batch(
                        n_tasks,
                        project=projects,
                        **{"account": account} if hasattr(models.Task, "account") else {},
                    )
                    tasks_count += len(tasks)

                    n_subtasks = FuzzyInteger(min_subtasks, max_subtasks).fuzz() * len(tasks)
                    subtasks = SubtaskFactory.create_batch(
                        n_subtasks,
                        task=tasks,
                        **{"account": account} if hasattr(models.Subtask, "account") else {},
                    )
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
