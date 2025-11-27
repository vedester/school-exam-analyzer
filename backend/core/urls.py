# backend/core/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User # Import User model

# Import JWT views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# --- 1. THE EMERGENCY SUPERUSER CREATOR ---
# Visits to this link will create an admin user automatically
def create_superuser_view(request):
    try:
        # Check if admin already exists
        if User.objects.filter(username='admin').exists():
            return HttpResponse("Admin user already exists! Login with 'admin' and your chosen password.")
        
        # Create the user
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        return HttpResponse("✅ Success! Superuser created.<br>Username: <b>admin</b><br>Password: <b>admin123</b><br><br><b>IMPORTANT:</b> Now delete this code from urls.py!")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

# Simple view for the homepage so it doesn't look broken
def home_view(request):
    return JsonResponse({
         
        "status": "Online 🚀😂😂",
        "message": "School Analytics API is running successfully.😎😋",
        "endpoints": {
            "upload_exam": "/api/analytics/exam-uploads/",
            "admin": "/admin/"
        }
    })

urlpatterns = [
    # 0. Homepage (Fixes the "Not Found" error)
    path('', home_view),

    path('make-me-admin/', create_superuser_view),

    path('admin/', admin.site.urls),
    
    # 1. Analytics API
    path('api/analytics/', include('analytics.urls')),

    # 2. Authentication Endpoints
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 3. FORCE MEDIA SERVING (Critical for Render Free Tier)
    # This tells Django to serve files from the 'media' folder even if DEBUG=False
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]