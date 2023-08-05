import os
from pathlib import Path

from configurations import Configuration
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).parent.parent


class _NOT_PROVIDED:
    pass


def get_env_setting(env_var: str | list[str], default=_NOT_PROVIDED):
    """
    Get an environment setting or raise an exception if no default was specified
    :param env_var: enviroment variable or list of environment variables; will return the value of the first found (even if value is empty)
    :param default:
    """
    if default is not _NOT_PROVIDED and default is not None and not isinstance(default, str):
        # we enforce this to avoid unexpected type errors when env vars are actually set;
        # an env var value will always be a string
        # we allow None to indicate that something wasn't present
        raise ImproperlyConfigured("get_env_setting default values must be strings")

    env_vars = [env_var] if isinstance(env_var, str) else env_var

    x = default
    for env_var in env_vars:
        if env_var in os.environ:
            x = os.environ[env_var]
            break
    if x is _NOT_PROVIDED:
        error_msg = "Environment variable(s) %s not set" % (", ".join(env_vars))
        raise ImproperlyConfigured(error_msg)
    return x


class _Common(Configuration):
    INSTALLED_APPS = [
        "common",

        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        # 'django.contrib.staticfiles',
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "django_site.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    # WSGI_APPLICATION = 'django_site.wsgi.application'

    LANGUAGE_CODE = "en-au"
    TIME_ZONE = get_env_setting("TZ")
    USE_I18N = True
    USE_TZ = True

    # STATIC_URL = 'static/'

    # DO NOT EVER USE THIS ON A PRODUCTION SITE
    # This is a VERY weak password hash, but it allows us to create lots of test users extremely quickly
    PASSWORD_HASHERS = ("django.contrib.auth.hashers.UnsaltedSHA1PasswordHasher",)

    DEBUG = True


class MultipleDb(_Common):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": get_env_setting("PGHOST", "localhost"),
            "NAME": get_env_setting("PGDATABASE"),
            "PORT": get_env_setting("PGPORT", "5432"),
            "USER": get_env_setting(["PGUSER", "USER"]),
            "PASSWORD": get_env_setting("PGPASSWORD", None),
        }
    }

    MODELS_MODULE = "multidb"

    AUTH_USER_MODEL = "multidb.User"

    INSTALLED_APPS = _Common.INSTALLED_APPS + [
        "multidb",
    ]