from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import (
    UserRegistrationView, 
    PasswordResetRequestView, 
    PasswordResetConfirmView,
    CustomTokenObtainPairView,
    UserProfileView
)

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='logout'),
    
    # Password reset endpoints
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]
