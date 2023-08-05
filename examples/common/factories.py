from datetime import datetime
import importlib
from typing import Any
import zoneinfo

from django.conf import settings
from factory import Faker
from factory import lazy_attribute
from factory import LazyAttributeSequence
from factory import post_generation
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDateTime


models = importlib.import_module(settings.MODELS_MODULE + ".models")

tzinfo = zoneinfo.ZoneInfo(settings.TIME_ZONE)


class AccountFactory(DjangoModelFactory):

    class Meta:
        model = models.Account

    @post_generation
    def post(obj: models.Account, create: bool, extracted: Any, **kwargs):
        obj.slug = f"tenant-{obj.id}"
        obj.save()


class UserFactory(DjangoModelFactory):
    # account = ...
    email = LazyAttributeSequence(lambda obj, n: f'{obj.first_name}-{obj.last_name}-{n}@example.com')
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    is_active = True
    date_joined = FuzzyDateTime(datetime(2020, 1, 1, tzinfo=tzinfo))

    # we jump through some hoops here to ensure that the unencrypted password is available to
    # test cases that may want to use it to log in
    @post_generation
    def password(record: models.User, create: bool, extracted: str | None, **kwargs):
        if extracted is not None:
            password = extracted
        else:
            password = models.User.objects.make_random_password()
        record.set_password(password)
        record._unencrypted_password = password

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        super()._after_postgeneration(instance, create, results)
        if create:
            # restore _password since save() wipes it
            instance._password = instance._unencrypted_password
            delattr(instance, "_unencrypted_password")

    class Meta:
        model = models.User


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = models.Project


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = models.Task


class SubtaskFactory(DjangoModelFactory):
    class Meta:
        model = models.Subtask
