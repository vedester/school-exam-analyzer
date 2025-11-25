#backend/core/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # connect our analytics app API urls
    path('api/', include('analytics.urls')),
]


# This allows us to serve the uploaded files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)