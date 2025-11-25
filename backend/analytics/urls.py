#backend/analytics/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamUploadViewset

# we wi;ll then create a router and register our viewset with it
router = DefaultRouter()
router.register(r'uploads', ExamUploadViewset)

# the API URLS are now determined automacally by the router
urlpatterns = [
    path('', include(router.urls)),
]