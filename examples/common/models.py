from django.contrib.auth.models import AbstractUser
from django.db.models import AutoField
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import EmailField
from django.db.models import Model
from django.db.models import TextField

# This contains the base model definitions
#
# Due to differences in implementation, foreign keys need to be defined in the concrete models


class Account(Model):
    id = AutoField(primary_key=True)
    slug = CharField(max_length=255, unique=True)
    name = CharField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return f"Account #{self.id}" if self.id else "New Account"


class User(AbstractUser):
    id = AutoField(primary_key=True)
    # account -- FK
    email = EmailField(unique=True)

    # we're going to use email rather than username for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username = None
    # wipe out some of the inherited fields that we don't want
    is_staff = None
    groups = None
    user_permissions = None

    class Meta:
        abstract = True

    def __str__(self):
        return f"User #{self.id}" if self.id else "New User"


class Project(Model):
    id = AutoField(primary_key=True)
    # account -- FK
    name = CharField(max_length=255)
    details = TextField(blank=True, default="")

    class Meta:
        abstract = True

    def __str__(self):
        return f"Project #{self.id}" if self.id else "New Project"


class Task(Model):
    id = AutoField(primary_key=True)
    # project -- FK
    name = CharField(max_length=255)
    is_complete = BooleanField(default=False)
    details = TextField(blank=True, default="")

    class Meta:
        abstract = True

    def __str__(self):
        return f"Task #{self.id}" if self.id else "New Task"


class Subtask(Model):
    id = AutoField(primary_key=True)
    # task -- FK
    name = CharField(max_length=255)
    is_complete = BooleanField(default=False)
    details = TextField(blank=True, default="")

    class Meta:
        abstract = True

    def __str__(self):
        return f"Subtask #{self.id}" if self.id else "New Subtask"
