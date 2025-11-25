#backend/core/urls.py

from django.contrib import admin
from django.urls import path, include,re_path
from django.conf import settings

from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    # connect our analytics app API urls
    path('api/', include('analytics.urls')),


    # Add this block to serve media files in production

    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),

    
]


# This allows us to serve the uploaded files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)