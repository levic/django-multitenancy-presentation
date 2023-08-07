from collections.abc import Sequence
from datetime import datetime
import importlib
from typing import Any
import zoneinfo

from django.conf import settings
from factory import Faker
from factory import LazyAttributeSequence
from factory.declarations import Transformer
from factory.django import DjangoModelFactory
from factory.django import Password
from factory.fuzzy import FuzzyChoice
from factory.fuzzy import FuzzyDateTime


models = importlib.import_module(settings.MODELS_MODULE + ".models")

tzinfo = zoneinfo.ZoneInfo(settings.TIME_ZONE)


def select_random(value: Any):
    """
    Transformer that picks randomly:
    - if not a list then it will just use that value directly
    - if a list then it will pick a random item from the list
    """
    if isinstance(value, Sequence):
        value = FuzzyChoice(value).fuzz()
    return value


class AccountFactory(DjangoModelFactory):
    slug = LazyAttributeSequence(lambda obj, n: f"tenant-{n}")
    name = Faker("company")

    class Meta:
        model = models.Account


class UserFactory(DjangoModelFactory):
    account = Transformer(None, transform=select_random)
    email = LazyAttributeSequence(lambda obj, n: f"{obj.first_name}-{obj.last_name}-{n}@example.com")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    is_active = True
    date_joined = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=tzinfo))
    password = Password("password")

    class Meta:
        model = models.User


class ProjectFactory(DjangoModelFactory):
    account = Transformer(None, transform=select_random)
    name = LazyAttributeSequence(lambda obj, n: f"project-{n}")
    details = Faker("paragraph")

    class Meta:
        model = models.Project


class TaskFactory(DjangoModelFactory):
    project = Transformer(None, transform=select_random)
    name = Faker("text", max_nb_chars=200)
    is_complete = FuzzyChoice([True, False])
    details = Faker("paragraph")

    class Meta:
        model = models.Task


class SubtaskFactory(DjangoModelFactory):
    task = Transformer(None, transform=select_random)
    name = Faker("text", max_nb_chars=200)
    is_complete = FuzzyChoice([True, False])
    details = Faker("paragraph")

    class Meta:
        model = models.Subtask
