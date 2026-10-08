"""
Root URL configuration for skincare_clinic project.
Includes technical SEO routes: sitemap.xml and robots.txt.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import sitemaps
from core import views as core_views

# Customize Django Admin
admin.site.site_header = 'Skin & Hair Care Clinic — Administration'
admin.site.site_title = 'Clinic Admin'
admin.site.index_title = 'Dashboard'

admin_path = getattr(settings, 'ADMIN_URL', 'admin/').strip('/') + '/'

urlpatterns = [
    path(admin_path, admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', core_views.robots_txt, name='robots_txt'),
    path('', include('core.urls')),
    path('treatments/', include('treatments.urls')),
    path('doctors/', include('doctors.urls')),
    path('appointments/', include('appointments.urls')),
    path('blog/', include('blog.urls')),
    path('gallery/', include('gallery.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'
