"""
WSGI config for snakeoil project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import sys
from django.core.wsgi import get_wsgi_application

sys.path.append('/opt/bitnami/projects/snake-oil-webshop')

application = get_wsgi_application()
