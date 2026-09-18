"""
URL routing configuration for the quiz management endpoints.
Uses a Django REST Framework DefaultRouter to automatically generate routes for the QuizViewSet.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuizViewSet


router = DefaultRouter()
router.register(r'', QuizViewSet, basename='quiz')

urlpatterns = [
    path('', include(router.urls)),
]