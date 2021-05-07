"""
WSGI config for snakeoil project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import sys
import os
from django.core.wsgi import get_wsgi_application

sys.path.append('/opt/bitnami/projects/snake-oil-webshop')
os.environ.setdefault("PYTHON_EGG_CACHE", "/opt/bitnami/projects/snake-oil-webshop/egg_cache")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snakeoil.settings")

application = get_wsgi_application()
