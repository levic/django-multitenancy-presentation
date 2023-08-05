"""
WSGI config for django_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from configurations.wsgi import get_wsgi_application
from dotenv import load_dotenv


load_dotenv(Path(__file__).parent / "env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_site.settings")
# os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

application = get_wsgi_application()
