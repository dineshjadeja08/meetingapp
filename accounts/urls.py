from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import (
    UserRegistrationView, 
    PasswordResetRequestView, 
    PasswordResetConfirmView,
    CustomTokenObtainPairView,
    UserProfileView
)
from .oauth_views import (
    GoogleOAuthTokenView,
    GoogleOAuthInitView,
    SocialAccountStatusView
)

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/register/', UserRegistrationView.as_view(), name='auth_register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='logout'),
    
    # Google OAuth endpoints - Custom API endpoints
    path('auth/google/init/', GoogleOAuthInitView.as_view(), name='google_oauth_init'),
    path('auth/google/token/', GoogleOAuthTokenView.as_view(), name='google_oauth_token'),
    path('auth/social/status/', SocialAccountStatusView.as_view(), name='social_account_status'),
    
    # Password reset endpoints
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]
