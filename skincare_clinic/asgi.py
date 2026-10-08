"""
ASGI config for skincare_clinic project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skincare_clinic.settings')
application = get_asgi_application()
