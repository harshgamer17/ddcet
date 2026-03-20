"""
URL configuration for ddcetpro1 project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Django Admin
    path('admin/', admin.site.urls),

    # App URLs
    path('', include('ddcetapp1.urls')),

    # ✅ FAVICON FIX (IMPORTANT)
    path(
        'favicon.ico',
        RedirectView.as_view(
            url='/static/images/favicon.ico',
            permanent=True
        )
    ),
]

# ✅ Serve static files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
