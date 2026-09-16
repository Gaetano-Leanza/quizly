"""
URL routing configuration for the authentication endpoints.
Maps URLs to their respective API views for registration, login, logout, and token refresh.
"""

from django.urls import path
from .views import RegisterView, LoginView, LogoutView, CookieTokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
]