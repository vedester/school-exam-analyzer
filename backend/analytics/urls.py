#backend/analytics/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamUploadViewSet, RegisterView

# we wi;ll then create a router and register our viewset with it
router = DefaultRouter()
router.register(r'exam-uploads', ExamUploadViewSet, basename='exam-upload')

# the API URLS are now determined automacally by the router
urlpatterns = [
    path('', include(router.urls)),
    # Add any additional endpoints here
    path('register/', RegisterView.as_view(), name='auth_register'), # <--- New Endpoint

]