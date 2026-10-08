"""
WSGI config for skincare_clinic project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skincare_clinic.settings')
application = get_wsgi_application()
